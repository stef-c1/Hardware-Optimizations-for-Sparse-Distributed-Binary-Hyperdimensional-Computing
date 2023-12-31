% Function Name: distances_AM_sparse
%
% Description: Calculates cosine similarity between any two classes in AM
%
% Arguments:
%   AM - associative memory containing gesture classes
% 
% Returns:
%   distances - element (i, j) shows cosine similarity b/w classes i & j
%

function [distances] = distances_AM_sparse(AM)
    classes = AM.keys;
    for i = 1:1:size(classes, 2)
        for j = 1:1:size(classes, 2)
            distances(i, j) = sparse_similarity(AM(cell2mat(classes(i))), AM(cell2mat(classes(j))));
        end
    end
end