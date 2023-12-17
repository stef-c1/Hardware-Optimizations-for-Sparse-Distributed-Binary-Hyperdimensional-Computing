module gen_rand_index #(
    parameter RANGE = 64;
)
(
    input  logic clk,
    input  logic arst_n_in,
    output logic [$clog2(RANGE)-1:0] pseudo_rand_nb
);

//this part is pipelined so as to keep the clock cycle time low
//a new "random" number is provided every cycle whether it is used or not
//to construct a "random" number, 2 steps are required: first construct 4*previous_nb+1, then add this to the previous_nb to get 5*previous_nb+1
//this operation varies uniformly over the whole range, starting from a seed

reg [$clog2(RANGE)-1:0] el1 = RANGE-2;

reg [$clog2(RANGE)-1:0] el2a = 1;
reg [$clog2(RANGE)-1:0] el2b = 0;

wire [$clog2(RANGE)-1:0] el1a;
wire [$clog2(RANGE)-1:0] el1b;
wire [$clog2(RANGE)-1:0] el2;

always_comb begin
    el1a = el1<<2;
    el1a[0] = 1;
    el1b = el1;

    el2 = el2a+el2b;
end

always @(posedge clk) begin
    el1 <= el2;
    el2a <= el1a;
    el2b <= el1b;
end

