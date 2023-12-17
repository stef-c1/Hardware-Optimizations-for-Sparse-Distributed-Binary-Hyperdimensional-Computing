% Function Name: randomHV_sparse
%
% Description: Generates a sparse random hypervector of 1's and 0's
%
% Arguments:
%   D - hypervector dimension
%   p - probability of a 1
% 
% Returns:
%   randomHV - generated random hypervector
% 

function randomHV = gen_random_HV_sparse(D,p)

    if mod(D, 2)
        disp('Dimension is odd!!');
    else
        % generate a random vector of indices
        randomIndex = randperm(D);

        randomHV(randomIndex(1:D*p)) = 1;
        randomHV(randomIndex(D*p+1:D)) = 0;
    end
end