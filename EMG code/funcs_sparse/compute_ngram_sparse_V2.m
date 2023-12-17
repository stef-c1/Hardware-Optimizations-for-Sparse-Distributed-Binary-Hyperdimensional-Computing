% Function Name: compute_ngram_sparse_V2
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

function [ngram] = compute_ngram_sparse_V2(buffer, eM, vM, model, nb_quantization_levels)
    ngram = ones(1, model.D);
    s = zeros(1, model.D);


    q = quantizer([log2(nb_quantization_levels),log2(nb_quantization_levels)], 'ufixed', 'nearest');
    quantized_buffer = quantize(q,buffer);

    %quantized_values_list = 0:1/nb_quantization_levels:1;
    quantized_values_list = 0:1/nb_quantization_levels:1;
    
    for t = 1:model.N
        for e = 1:model.noCh
            % disp(quantized_buffer(e,t));
            % disp(find(quantized_values_list == quantized_buffer(e,t)));
            % pause()

            hv_buffer_value = vM(find(quantized_values_list == quantized_buffer(e,t))); %#ok<FNDSB>
            s = s + segm_shift_binding(eM(e), hv_buffer_value, model.D, model.p_sparse); %binding for sparse
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