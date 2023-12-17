module u_gen_rand_hv_sparse #(
    parameter int D = 1024,
    parameter int LENGTH_SEGMENT = 32,
    parameter int NB_OF_SEGMENTS = 32
)
(
    input  logic clk,
    input  logic arst_n_in,
    input  logic start_new_hv,
    output logic [LENGTH_SEGMENT-1:0] segment_hv_output,
    output logic out_sgmnt_ready 
)


logic [$clog2(NB_OF_SEGMENTS)-1:0] segment_counter;


typedef enum {IDLE, WAIT, SEND_OUTPUTS} fsm_state;
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

gen_rand_index #(.RANGE(LENGTH_SEGMENT))
gen0 (.clk(clk), .arst_n_in(arst_n_in), .pseudo_rand_nb(gen0_out));


always_comb begin
    start_ss_bb0 = 0;
    out_sgmnt_ready = 0;
    case(current_state)
        IDLE: begin
            next_state = (start_new_hv) ? CONSTRUCT_VECTOR : IDLE;
            segment_hv_output <= 0;
        end
        CONSTRUCT_VECTOR: begin
            segment_hv_output[gen0_out] <= 1;
            next_state = SEND_OUTPUTS;
        end
        SEND_OUTPUTS: begin
            out_sgmnt_ready = 1;
            segment_counter <= segment_counter+1;
            next_state =  (segment_counter == NB_OF_SEGMENTS-1) ? IDLE : CONSTRUCT_VECTOR;
        end
    endcase
end