module ss_basic_block #(
    parameter LENGTH_VECTOR = 32
)
(
    input  logic clk,
    input  logic arst_n_in,
    input  logic [LENGTH_VECTOR-1:0] hv_a, //can logic here, work as a nice register? if not, make actual regs and write inputs into them.
    input  logic [LENGTH_VECTOR-1:0] hv_b,
    input  logic start,
    output logic done,
    output logic [LENGTH_VECTOR-1:0] hv_out
);

parameter LENGTH_COUNTER = $clog2(LENGTH_VECTOR)

logic [LENGTH_COUNTER-1:0] shift_counter;



typedef enum {IDLE, FIND_SHIFT, SHIFTING, DONE} fsm_state;
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
    case (current_state)
      IDLE: begin
        next_state = (start) ? FIND_SHIFT : IDLE;
        shift_counter = 0;
      end
      FIND_SHIFT: begin
        hv_a <= hv_a >> 1;
        if (hv_a == 1) begin
            next_state = SHIFTING;
        end
        else begin
            shift_counter <= shift_counter+1;
            next_state = FIND_SHIFT;
        end
      end
      SHIFTING: begin
        if (shift_counter == 0) begin
            //if in 0'th place, do we shift? if so, do another shift here
            next_state = DONE;
        end
        else begin
            hv_b <= hv_b << 1;
            shift_counter <= shift_counter-1;
            next_state = SHIFTING;
        end
      end
      DONE: begin
        done = 1;
        next_state = IDLE;
        hv_out = hv_b;
      end
      default: next_state = IDLE;
    endcase
end