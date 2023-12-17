% Function Name: sparse_similarity
%
% Description: Calculates the sparse similarity between two hypervectors
%
% Arguments:
%   u - first hypervector
%   v - second hypervector
% 
% Returns:
%   sim - the sparse similarity between u and v (between -1 and 1)
%

function sim = sparse_similarity(u, v)
    sim = 0;
    for i = 1:length(u)
        if (u(i) == 1 && v(i) == 1)
            sim = sim+1;
        end
    end
    sim = sim/length(u);
end
