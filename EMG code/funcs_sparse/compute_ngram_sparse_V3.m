% Function Name: compute_ngram_sparse_V3
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

function [ngram] = compute_ngram_sparse_V3(buffer, eM, model)
    ngram = ones(1, model.D);
    s = zeros(1, model.D);

    
    for t = 1:model.N
        for e = 1:model.noCh
            if (buffer(e,t) > 1)
                factor_of_presentness = 8;
            elseif (buffer(e,t) > 0.75)
                factor_of_presentness = 4;
            elseif (buffer(e,t) > 0.5)
                factor_of_presentness = 2;
            elseif (buffer(e,t) > 0.25)
                factor_of_presentness = 1;
            else 
                factor_of_presentness = 0;
            end
            s = s + eM(e)*factor_of_presentness;
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