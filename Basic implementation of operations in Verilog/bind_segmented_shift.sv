module bind_ss_basic #(
    parameter int D = 1024,
    parameter int LENGTH_SEGMENT = 32,
    parameter int NB_OF_SEGMENTS = 32
)
(
    input  logic clk,
    input  logic arst_n_in,
    input  logic start_new_hv,
    input  logic [LENGTH_SEGMENT-1:0] segment_hv_a,
    input  logic [LENGTH_SEGMENT-1:0] segment_hv_b,
    input  logic new_sgmnts_ready,
    output logic [LENGTH_SEGMENT-1:0] segment_hv_output,
    output logic out_sgmnt_ready 
)

//This module asks for the next segment of the hv and feeds it to the ss_basic_block, when this gives an output it writes this back and asks for the next segment.
//I envision the complete hv be stored in a register bank in the main file.
//This approach also lends itself to easier speed-up, if for example mutiple of these need to be done in parallel, just add more ss_basic_blocks in here, or if the topology needs to be changed, 
//just change the ss_basic_block and the widths of the signals. 
//We also work with segments here, as if we did not, there would be a lot of regs here all connected to the ss_basic_block, 
//this would lead to great capacitance on the input wires of the ss_basic_block and a slower clock cycle.

logic [$clog2(NB_OF_SEGMENTS)-1:0] segment_counter;


typedef enum {IDLE, SEND_SGMNTS, WAIT, SEND_OUTPUTS} fsm_state;
fsm_state current_state;
fsm_state next_state;

always @(posedge clk or negedge arst_n_in) begin
    if(arst_n_in == 0) begin
      //do a reset
    end
    else begin
      current_state <= next_state
    end
end

ss_basic_block #(.LENGTH_VECTOR(LENGTH_SEGMENT))
ss_bb0 (.clk(clk), .arst_n_in(arst_n_in), .hv_a(segment_hv_a), .hv_b(segment_hv_b), .start(start_ss_bb0), .done(done_ss_bb0), .hv_out(out_ss_bb0));


always_comb begin
    start_ss_bb0 = 0;
    out_sgmnt_ready = 0;
    case(current_state)
        IDLE: begin
            next_state = (start_new_hv) ? SEND_SGMNTS : IDLE;
        end
        SEND_SGMNTS: begin
            start_ss_bb0 = (new_sgmnts_ready) ? 1:0;
            next_state = WAIT;
        end
        WAIT: begin
            next_state = (done_ss_bb0) ? SEND_OUTPUTS : WAIT;
            segment_hv_output <= (done_ss_bb0) ? out_ss_bb0 : segment_hv_output;
        end
        SEND_OUTPUTS: begin
            out_sgmnt_ready = 1;
            segment_counter <= segment_counter+1;
            next_state =  (segment_counter == NB_OF_SEGMENTS-1) ? IDLE : SEND_SGMNTS;
        end
    endcase
end
