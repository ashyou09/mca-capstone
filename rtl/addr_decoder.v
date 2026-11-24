// =============================================================================
// addr_decoder.v  (M2)
// Purpose : split a CPU byte address into tag / index / offset / word_sel
//           for a direct-mapped cache (plan.md 2, 4.3; docs/address_breakdown.md).
// Ports   : addr[ADDR_W-1:0] in  ->  tag, index, offset, word_sel out.
// Timing  : purely combinational (only wires, no state, no clock).
//
//   | tag (TAG_W) | index (INDEX_W) | offset (OFF_W) |
//                                    \_ word_sel = offset[OFF_W-1:2]
//
// All widths come from the parameters via $clog2, so nothing is hard-coded.
// Requirements: CACHE_BYTES and BLOCK_BYTES are powers of 2,
//               BLOCK_BYTES >= 8 (at least 2 words), CACHE_BYTES >= 2*BLOCK_BYTES.
// =============================================================================
// 'module' = creates a hardware block (like a chip with pins)

// addr_decoder (The Address Slicer): Cuts the 32-bit CPU address into three parts: tag, index [9:4], 
// and word_sel [3:2]. It is pure copper wiring, so it uses 0 logic cells.

module addr_decoder #(
    // 'parameter' = settings you can change from outside before building
    parameter ADDR_W      = 32,
    parameter CACHE_BYTES = 1024,
    parameter BLOCK_BYTES = 16
) (
    // 'input wire' = physical wire bringing signals INTO this block
    input  wire [ADDR_W-1:0]                          addr,
    
    // 'output wire' = physical wire sending signals OUT to other blocks
    output wire [ADDR_W-$clog2(CACHE_BYTES)-1:0]      tag,
    output wire [$clog2(CACHE_BYTES/BLOCK_BYTES)-1:0] index,
    output wire [$clog2(BLOCK_BYTES)-1:0]             offset,
    output wire [$clog2(BLOCK_BYTES)-3:0]             word_sel
);

    // 'localparam' = fixed internal math constants (cannot be changed from outside)
    localparam NUM_LINES = CACHE_BYTES / BLOCK_BYTES;
    localparam OFF_W     = $clog2(BLOCK_BYTES);      // '$clog2' = log base 2 (finds how many bits we need)
    localparam INDEX_W   = $clog2(NUM_LINES);
    localparam TAG_W     = ADDR_W - INDEX_W - OFF_W;

    // 'assign' = permanently connects an input wire directly to an output wire (pure copper connection, no clock)
    assign offset   = addr[OFF_W-1:0];
    assign index    = addr[OFF_W+INDEX_W-1:OFF_W];
    assign tag      = addr[ADDR_W-1:OFF_W+INDEX_W];
    assign word_sel = addr[OFF_W-1:2];

endmodule
