// =============================================================================
// tag_ram.v  (M2)
// Purpose : store the tag of the block currently held in each cache line.
// Size    : 2^INDEX_W entries x TAG_W bits.
// Ports   : read  -> index, tag_out
//           write -> clk, we, w_index, w_tag
// Timing  : asynchronous (combinational) read, synchronous write on posedge clk.
//           A write is visible on tag_out from the next cycle.
//
// No reset: the contents do not matter while the line's valid bit is 0
// (valid_ram is reset, tag_ram is not). This also lets synthesis map it to
// distributed/LUT RAM instead of flip-flops with reset logic.
// =============================================================================

// tag_ram (The Name Tags): Stores a 22-bit ID tag for each of the 64 cache lines. 
// It reads instantly (asynchronously) without waiting for a clock, and has no reset 
// because tags are ignored when a line is invalid.

module tag_ram #(
    parameter INDEX_W = 6,
    parameter TAG_W   = 22
) (
    input  wire               clk,       // Clock for writing tags
    input  wire [INDEX_W-1:0] index,     // Drawer number (0-63) to read[cite: 1]
    output wire [TAG_W-1:0]   tag_out,   // 22-bit stored ID tag coming out[cite: 1]
    input  wire               we,        // Write Enable from Pankaj's FSM[cite: 1]
    input  wire [INDEX_W-1:0] w_index,   // Drawer number to update
    input  wire [TAG_W-1:0]   w_tag      // New 22-bit tag to save
);

    localparam DEPTH = 1 << INDEX_W;

    // 2D 'reg' array = 64 rows, each holding a 22-bit tag (no reset needed!)[cite: 1]
    reg [TAG_W-1:0] mem [0:DEPTH-1];

    // Instant (asynchronous) read: needed so hit check finishes in 1 cycle[cite: 1]
    assign tag_out = mem[index];

    // Synchronous write: saves the new tag only when FSM raises 'we' on clock tick[cite: 1]
    always @(posedge clk) begin
        if (we)
            mem[w_index] <= w_tag;
    end

endmodule
