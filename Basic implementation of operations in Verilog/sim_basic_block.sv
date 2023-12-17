module sim_basic_block #(
    parameter LENGTH_VECTOR = 32,
    parameter LENGTH_COUNTER = $clog2(LENGTH_VECTOR)
)
(
    input  logic clk,
    input  logic arst_n_in,
    input  logic [LENGTH_VECTOR-1:0] hv_a, 
    input  logic [LENGTH_VECTOR-1:0] hv_b,
    input  logic start,
    output logic done,
    output logic [LENGTH_COUNTER-1:0] counter_out
);

logic [LENGTH_COUNTER-1:0] counter_over_vector;

typedef enum {IDLE, COUNT_SIMILARITIES, DONE} fsm_state;
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


always_comb begin
    done = 0;
    case(current_state)
        IDLE: begin
            next_state = (start) ? COUNT_SIMILARITIES : IDLE;
            counter_out <= 0;
            counter_over_vector <= 0;
        end
        COUNT_SIMILARITIES: begin
            counter_out_we = hv_a[0] & hv_b[0];
            counter_out <= (counter_out_we) ? counter_out+1 : counter_out;
            hv_a <= hv_a >> 1;
            hv_b <= hv_b >> 1;
            counter_over_vector <= counter_over_vector+1;
            next_state = (counter_over_vector == LENGTH_VECTOR-1) ? DONE : COUNT_SIMILARITIES;
        end
        DONE: begin
            done = 1;
            next_state = IDLE;
        end
    endcase
end

