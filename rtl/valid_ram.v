// =============================================================================
// valid_ram.v  (M2)
// Purpose : one valid bit per cache line. valid=0 means "line is empty",
//           so the tag comparator must report a miss whatever the tag says.
// Size    : 2^INDEX_W x 1 bit.
// Ports   : read  -> index, valid_out
//           write -> clk, we, w_index, w_valid
//           rst_n -> active-low SYNCHRONOUS reset, clears every valid bit.
// Timing  : asynchronous read, synchronous write and reset (posedge clk).
//           Reset has priority over a write in the same cycle.
//
// Stored as a flat bit-vector (not a memory array) so that the whole thing
// can be cleared in one cycle. In hardware this is 2^INDEX_W flip-flops with
// a synchronous clear, plus a 2^INDEX_W:1 read mux.
// =============================================================================

// valid_ram (The Status Lights): Uses 64 flip-flops (1 bit per line) to show if a line holds real data (1) or empty garbage (0). 
// Using flip-flops lets one reset pulse wipe the whole cache clean in 1 cycle, and reset always beats a same-cycle write.

module valid_ram #(
    parameter INDEX_W = 6
) (
    input  wire               clk,       // System heartbeat clock (syncs all writes)[cite: 1]
    input  wire               rst_n,     // Active-low reset ('_n' means 0 triggers reset)[cite: 1]
    input  wire [INDEX_W-1:0] index,     // Drawer number (0-63) we want to read[cite: 1]
    output wire               valid_out, // 1-bit status light coming out (1=real, 0=empty)[cite: 1]
    input  wire               we,        // Write Enable: 1 = permission to save new bit
    input  wire [INDEX_W-1:0] w_index,   // Which drawer to write into
    input  wire               w_valid    // The new bit (1 or 0) to save
);

    // '1 << 6' shifts 1 left by 6 bits = 2^6 = 64 lines
    localparam DEPTH = 1 << INDEX_W;

    // 'reg' = actual storage (creates 64 physical flip-flops in hardware)[cite: 1]
    reg [DEPTH-1:0] valid_bits;

    // 'assign' = instant read (no clock wait; bit comes out as soon as index arrives)[cite: 1]
    assign valid_out = valid_bits[index];

    // 'always @(posedge clk)' = runs ONLY at the exact rising tick of the clock
    always @(posedge clk) begin
        if (!rst_n)
            // '{64{1'b0}}' = repeats '0' 64 times to wipe all lights clean in 1 cycle[cite: 1]
            valid_bits <= {DEPTH{1'b0}};
        else if (we)
            // '<=' = non-blocking assignment (updates storage cleanly on clock edge)
            valid_bits[w_index] <= w_valid;
    end

endmodule
