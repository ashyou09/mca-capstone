// =============================================================================
// tag_comparator.v  (M2)
// Purpose : decide hit/miss for the line selected by the index.
// Ports   : tag_a (stored tag from tag_ram), tag_b (tag of cpu_addr),
//           valid (valid bit of the line)  ->  hit.
// Timing  : purely combinational.
//
//   hit = valid & (tag_a == tag_b)
//
// The valid bit is mandatory: after reset the tag RAM holds garbage (or 0),
// so without it address 0x0 (tag 0) could falsely "hit" on an empty line.
// =============================================================================

// tag_comparator (The Hit Checker): Checks hit = valid & (stored_tag == requested_tag) using simple combinational logic.
// If both are true, it sends hit = 1 to Pankaj's controller in the exact same clock cycle.

module tag_comparator #(
    
    parameter TAG_W = 22
) (
    input  wire [TAG_W-1:0] tag_a, // 22-bit stored tag coming from tag_ram[cite: 1]
    input  wire [TAG_W-1:0] tag_b, // 22-bit requested tag coming from addr_decoder[cite: 1]
    input  wire             valid, // 1-bit status coming from valid_ram[cite: 1]
    output wire             hit    // 1-bit final result sent to Pankaj's FSM (1=hit, 0=miss)[cite: 1]
);

    // '==' checks if all 22 bits of tag_a and tag_b match (returns 1 if equal, 0 if not)[cite: 1]
    // '&' is bitwise AND: both 'valid' AND 'tags match' must be 1 for 'hit' to be 1[cite: 1]
    // Purely combinational: no clock wait, so hit is known in the exact same cycle[cite: 1]

    assign hit = valid & (tag_a == tag_b);

endmodule
