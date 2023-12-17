% Function Name: getacc
%
% Description: Trains and tests HD classifier. 
%
% Arguments:
%   subject - reference number for subject
%   N - length of ngram
%   numtrain - number of training trials to use
%   chan - subset of channels used for training and testing
%   dirtrain - directory containing training trials
%   dirtest - directory containing testing trials
% 
% Returns:
%   label - unvoted classifier output
%   correct - correct label command used during recording
%   accs - vector of classification accuracies for range of voting windows
%

function [out, correct, accs] = getacc(subject, N, numtrain, chan, dirtrain, dirtest)

    sparse = 1;
    
    % classify at the same rate as downsampling, i.e. every 100 ms
    classifyperiod = 100;
    downsampleperiod = 100;
    % window the data to get N samples after downsampling for an ngram
    windowsize = N*classifyperiod;
        
    % randomly select the number of trials used for training
    traintrial = randperm(10);
    traintrial = traintrial(1:numtrain);
    
    % gather training data
    rawtot = [];
    gesttot = [];
    twidth = 0.2; % percentage of data to throw out from each end of gesture segment
    for trial = traintrial
        % load the trial file
        fname = [num2str(subject,'%03.f') '-' num2str(trial,'%03.f')]; 
        load([dirtrain fname]);
        % generate labels for the data based on commands during recording
        gestlabel = genlabels(p,raw,twidth);
        % append to overall record
        rawtot = [rawtot; raw];
        gesttot = [gesttot gestlabel];
    end
    rawtrain = rawtot; % concatenated raw data from selected training trials
    gestlabeltrain = gesttot; % gesture labels for data, with -1 being unused
    
    % set maximum vote window to the length of each gesture
    votewin = round((1 - 2*twidth)*p.timegest/downsampleperiod/2); 
    
    % gather testing data
    rawtot = [];
    gesttot = [];
    for trial = 1:10
        % load the trial file
        fname = [num2str(subject,'%03.f') '-' num2str(trial,'%03.f')];
        load([dirtest fname]);
        % generate labels for the data based on commands during recording
        gestlabel = genlabels(p,raw,twidth);
        % append to overall record
        rawtot = [rawtot; raw];
        gesttot = [gesttot gestlabel];
    end
    rawtest = rawtot; % concatenated raw data from testing trials
    gestlabeltest = gesttot; % gesture labels for data, with -1 being unused
        
    % load preprocessing filter (generated using genfilter.m)
    load('prefilter');
    % convolve the first two filters as they are used in a single step
    % before taking the absolute value
    a1 = conv(a1, a2);
    b1 = conv(b1, b2);
    a2 = a3;
    b2 = b3;
    
    % remove unused channels from recording
    rawtrain = rawtrain(:,1:64);
    datalen = size(rawtrain,1);
    
    % loop through and filter the training data window by window to
    % approximate online behavior
    filtdata = zeros(size(rawtrain));
    for i = windowsize+1:windowsize:datalen-(2*windowsize)+1
        % select 3 times the window size to make sure edge effects of
        % filtering can be removed
        window = rawtrain(i-windowsize:i+(2*windowsize)-1,:);
        % preprocess the data
        window = filtfilt(b1,a1,window);
        window = abs(window);
        window = filtfilt(b2,a2,window);
        % keep only the middle window to remove edge effects
        filtdata(i:i+windowsize-1,:) = window(windowsize+1:2*windowsize,:);
    end
    
    % find minima and maxima of each channel for normalization
    lower = 100.*ones(1,64);
    upper = zeros(1,64);
    for k = 1:64
        lower(k) = min(filtdata(find(gestlabeltrain ~= -1),k));
        upper(k) = max(filtdata(find(gestlabeltrain ~= -1),k));
    end
    
    % scale the raw data to improve HD accuracy, and select subset of data
    HDscale = 10;
    datatrain = rawtrain(:,chan).*HDscale;
    datatest = rawtest(:,chan).*HDscale;
    lower = lower(chan);
    upper = upper(chan);

    % build model for HD processing
    model = struct;
    model.D = 10000; % dimension of hypervectors
    model.N = N; % size of ngram
    model.noCh = length(chan); % number of input channels
    
    model.p_sparse = 0.01;
    model.p_dense = 0.2; % 0.2 was nice for sparse V1

    % generate random hypervector for each channel
    eM = containers.Map ('KeyType','int32','ValueType','any');
    for e = 1:1:model.noCh
        if (sparse == 0)
            eM(e) = gen_random_HV(model.D);
        else
            eM(e) = gen_random_HV_sparse_V2(model.D, model.p_sparse);
        end
    end

    % generate CIM for quantized signal values
    nb_quantization_levels = 256;
    vM = gen_random_CIM(model.D, model.p_sparse, nb_quantization_levels, 6);


    % generate associative memory for gesture labels
    % -1 = no label (unused data)
    % 0 = rest
    AM = containers.Map('KeyType','int32','ValueType','any'); 
    for i = -1:p.numlabels
        AM(i) = zeros(1,model.D);
    end
        
    % train AM with training data
    d = datatrain;
    g = gestlabeltrain;
    datalen = length(g);

    % loop through and filter each window, then train by updating AM
    for i = windowsize+1:classifyperiod:datalen-(2*windowsize)+1
        % filter the window
        window = d(i-windowsize:i+(2*windowsize)-1,:);
        window = filtfilt(b1,a1,window);
        window = abs(window);
        window = filtfilt(b2,a2,window);
        % normalize the window 
        % would expect-> minima is now 0, maxima is now 1
        % this is not the case !!!!
        for k = 1:model.noCh
            window(:,k) = (window(:,k)-lower(k))./(upper(k)-lower(k));
        end
        % remove edge effects
        window = window(windowsize+1:2*windowsize,:);
        
        % downsample the window (and associated gesture label)
        window = downsample(window,downsampleperiod);
        gestwindow = downsample(g(i:i+windowsize-1),downsampleperiod);
        
        % compute Ngrams and add into the AM
        for t = 1:length(gestwindow)-model.N+1
            if (sparse == 0)
                ngram = compute_ngram(window(t:t+model.N-1,:)', eM, model);
            else
                ngram = compute_ngram_sparse(window(t:t+model.N-1,:)', eM, model);
                %ngram = compute_ngram_sparse_V2(window(t:t+model.N-1,:)', eM, vM, model, nb_quantization_levels);
                %ngram = compute_ngram_sparse_V3(window(t:t+model.N-1,:)', eM, model);
            end
            label = mode(gestwindow(t:t+model.N-1));
            AM(label) = AM(label) + ngram;
        end
    end
    
    % remove the unused label from AM
    remove(AM,-1);
    
    % bipolarize the AM
    if (sparse == 0)
        bipolarize_AM(AM);
    else 
        bipolarize_AM_sparse(AM, model.D, model.p_dense);
    end

    
    %disp(distances_AM_sparse(AM));


    % test classifier on testing data
    accs = zeros(votewin+1,1);
    
    d = datatest;
    g = gestlabeltest;
    datalen = length(g);
    testlabel = zeros(size(g)); % vector of classifier output labels
    
    % loop though, window data, classify gesture
    for i = windowsize+1:classifyperiod:datalen-(2*windowsize)+1
        % filter the window
        window = d(i-windowsize:i+(2*windowsize)-1,:);
        window = filtfilt(b1,a1,window);
        window = abs(window);
        window = filtfilt(b2,a2,window);
        % normalize the window
        for k = 1:model.noCh
            window(:,k) = (window(:,k)-lower(k))./(upper(k)-lower(k));
        end
        % remove edge effects
        window = window(windowsize+1:2*windowsize,:);
        
        % downsample the window (and associated gesture label)
        window = downsample(window,downsampleperiod);
        gestwindow = downsample(g(i:i+windowsize-1),downsampleperiod);
        
        % calculate and accumulate ngrams for the window
        ngram = zeros(1,model.D);
        for t = 1:length(gestwindow)-model.N+1
            if (sparse == 0)
                ngram = ngram + compute_ngram(window(t:t+model.N-1,:)', eM, model);
            else
                ngram = ngram + compute_ngram_sparse(window(t:t+model.N-1,:)', eM, model);
                %ngram = ngram + compute_ngram_sparse_V2(window(t:t+model.N-1,:)', eM, vM, model, nb_quantization_levels);
                %ngram = ngram + compute_ngram_sparse_V3(window(t:t+model.N-1,:)', eM, model);
            end
        end
        
        % calculate closest gesture within AM
        if (sparse == 0)
            [maxSim, l] = find_closest_class(ngram, AM);
        else
            [maxSim, l] = find_closest_class_sparse(ngram, AM);
        end
        
        % update the output label
        testlabel(i:i+windowsize-1) = l;
    end

    % vote on the labels with range of voting windows
    correct = downsample(g,downsampleperiod); % correct labels
    out = downsample(testlabel,downsampleperiod); % voted labels
    
    % unused data shouldn't be included in accuracy measure
    testpoints = find(correct ~= -1);
    
    % loop through voting windows
    for i = 0:votewin %goes from very small to very wide window
        % create vector of voted labels
        vote = zeros(size(out));
        % account for edges where full vote windows aren't possible
        vote(1:i) = mode(out(1:2*i+1));
        vote(end-i+1:end) = mode(out(end-2*i:end));
        % vote over the rest of the full voting windows
        for k = i+1:length(vote)-i
            vote(k) = mode(out(k-i:k+i));
        end
        % calculate accuracy as the percentage of matches over all the used
        % testpoints
        accs(i+1) = sum(correct(testpoints) == vote(testpoints))/length(testpoints);
    end
end