% Function Name: compute_ngram_sparse
%
% Description: Generates the spatiotemporal encoded ngram for a window of
% EMG data (Fig. 3 in the paper)
%
% Arguments:
%   buffer - window of data to be encoded
%   eM - electrode memory, i.e. random hypervectors for each electrode
%   model - struct containing model parameters such as hypervectors
%   dimension, ngram size, and number of channels
% 
% Returns:
%   ngram - spatiotemporal encoded hypervector
%

function [ngram] = compute_ngram_sparse(buffer, eM, model)
    ngram = ones(1, model.D);
    s = zeros(1, model.D);
    for t = 1:model.N
        for e = 1:model.noCh
            s = s + eM(e) .* buffer(e, t); %normal multiplication, can stay for now
        end
        
        % sigma now makes D*p_dense highest '1', rest '0'
        [~, indexes] = maxk(s, round(model.D*model.p_dense));
        s(:) = 0;
        for j = 1:length(indexes)
            s(indexes(j)) = 1;
        end
        
        ngram = xor(ngram, (circshift(s, [0, model.N - t]))); %binding needs to become xor
    end
end