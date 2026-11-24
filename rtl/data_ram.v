// =============================================================================
// data_ram.v  (M2)
// Purpose : hold the cached data blocks.
// Size    : 2^INDEX_W lines x (BLOCK_BYTES*8) bits.
// Ports   : read  -> index, rd_block (whole block; cache_top picks the word)
//           write -> clk, we, w_index, w_word_sel, w_word[31:0]
// Timing  : asynchronous read of the full block, synchronous WORD-granular
//           write on posedge clk: only word w_word_sel of line w_index is
//           updated, the other words of that block keep their value.
// Word w of a block sits at bits [w*32+31 : w*32] (word 0 = lowest address).
// w_word_sel width = $clog2(BLOCK_BYTES) - 2  (plan.md 4.3).
// No reset: contents are only used when the line is valid.
// =============================================================================

// data_ram (The Data Shelves): Stores the actual data across 64 lines × 128 bits (4 words per line). 
// It reads an entire 128-bit block at once, while writing one 32-bit word at a time during memory refills.

module data_ram #(
    parameter INDEX_W     = 6,
    parameter BLOCK_BYTES = 16
) (
    input  wire                           clk,        // System clock (syncs all writes)[cite: 1]
    input  wire [INDEX_W-1:0]             index,      // Drawer number (0-63) to read[cite: 1]
    output wire [BLOCK_BYTES*8-1:0]       rd_block,   // Whole 128-bit shelf sent out to Word MUX[cite: 1]
    input  wire                           we,         // Write Enable from Pankaj's FSM[cite: 1]
    input  wire [INDEX_W-1:0]             w_index,    // Which drawer to write into
    input  wire [$clog2(BLOCK_BYTES)-3:0] w_word_sel, // Picks word slot 0, 1, 2, or 3 inside shelf[cite: 1]
    input  wire [31:0]                    w_word      // Single 32-bit word arriving from memory/CPU[cite: 1]
);

    localparam DEPTH      = 1 << INDEX_W;      // 64 cache lines[cite: 1]
    localparam BLOCK_BITS = BLOCK_BYTES * 8;   // 16 bytes * 8 = 128 bits per shelf[cite: 1]

    // 2D 'reg' memory: 64 shelves, each 128 bits wide[cite: 1]
    reg [BLOCK_BITS-1:0] mem [0:DEPTH-1];

    // Instant (async) read: dumps all 128 bits immediately; Word MUX picks 32 bits later[cite: 1]
    assign rd_block = mem[index];

    // Synchronous write: updates ONLY ONE 32-bit word inside the 128-bit shelf on clock tick[cite: 1]
    always @(posedge clk) begin
        if (we)
            // '[start +: width]' = indexed part-select!
            // If w_word_sel = 0 -> writes bits [31:0]
            // If w_word_sel = 1 -> writes bits [63:32]
            // If w_word_sel = 2 -> writes bits [95:64]
            // If w_word_sel = 3 -> writes bits [127:96]
            mem[w_index][w_word_sel*32 +: 32] <= w_word;
    end

endmodule
