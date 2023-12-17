% Function Name: bipolarize_AM_sparse
%
% Description: Bipolarizes all hypervectors in the AM, i.e. the highest 
% D*p_AM elements become 1, the others 0
%
% Arguments:
%   AM   - The associative memory to be bipolarized
%   D    - Dimension of the hypervectors
%   p_AM - normalized density for a '1' in the AM hypervectors
% 
% Returns:
%   None
%

function [] = bipolarize_AM_sparse(AM, D, p_AM)
    classes = AM.keys;
    for i = 1:1:size(classes, 2)
        temp = AM(cell2mat(classes(i)));
        [~, indexes] = maxk(temp, round(D*p_AM));
        temp(:) = 0;
        for j = 1:length(indexes)
            temp(indexes(j)) = 1;
        end
        AM(cell2mat(classes(i))) = temp;
    end
end