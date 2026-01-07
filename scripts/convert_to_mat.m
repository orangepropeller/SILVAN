function convert_to_mat()
    %CONVERT_TO_MAT Converts graph text files to Matlab .mat files with sparse adjacency matrix 'x'.
    
    scriptPath = fileparts(mfilename('fullpath'));
    datasetPath = fullfile(scriptPath, '..', 'datasets');
    csvPath = fullfile(scriptPath, 'graphs_experiments.csv');
    
    if ~isfile(csvPath)
        error('graphs_experiments.csv not found at %s', csvPath);
    end
    
    opts = detectImportOptions(csvPath);
    opts.Delimiter = ';';
    opts.VariableNamingRule = 'preserve';
    T = readtable(csvPath, opts);
    
    matDir = fullfile(datasetPath, 'mat');
    if ~isfolder(matDir)
        mkdir(matDir);
    end
    
    numGraphs = height(T);
    
    parfor i = 1:numGraphs
        try
            fName = T.graph_name{i};
            if iscell(fName)
                fName = fName{1};
            end
            
            dirVal = T.directed{i};
            if iscell(dirVal)
                dirVal = dirVal{1};
            end
            isDirected = strcmpi(strtrim(dirVal), 'D');
            
            inputFile = fullfile(datasetPath, fName);
            [~, name, ~] = fileparts(fName);
            outputFile = fullfile(matDir, [name, '.mat']);
            
            fprintf('Processing %s...\n', fName);
            
            if ~isfile(inputFile)
                warning('File not found: %s', inputFile);
                continue;
            end
            
            rawText = fileread(inputFile);
            lines = strsplit(rawText, '\n');
            
            numLines = length(lines);
            u = zeros(numLines, 1);
            v = zeros(numLines, 1);
            edgeCount = 0;
            
            for j = 1:numLines
                line = strtrim(lines{j});
                if ~isempty(line) && line(1) ~= '#'
                    nums = sscanf(line, '%f %f');
                    if length(nums) >= 2
                        edgeCount = edgeCount + 1;
                        u(edgeCount) = nums(1);
                        v(edgeCount) = nums(2);
                    end
                end
            end
            
            u = u(1:edgeCount);
            v = v(1:edgeCount);
        
            if isempty(u)
                warning('No data found in %s', fName);
                continue;
            end
            
            selfLoops = (u == v);
            u(selfLoops) = [];
            v(selfLoops) = [];
            
            if isempty(u)
                warning('Only self-loops found in %s', fName);
                continue;
            end
            
            [uniqueNodes, ~, ic] = unique([u; v]);
            numEdges = length(u);
            u_mapped = ic(1:numEdges);
            v_mapped = ic(numEdges+1:end);
            
            n = length(uniqueNodes);
            
            x = sparse(u_mapped, v_mapped, true, n, n);
            
            if ~isDirected
                x = triu(x, 1) | tril(x, -1);
                x = x + x';
            end
            
            x = logical(x);
            
            parsave(outputFile, x, isDirected);
            
            numEdges = nnz(x);
            if ~isDirected
                numEdges = numEdges / 2;
            end
            fprintf('Completed %s: %d nodes, %d edges\n', fName, n, numEdges);
        catch ME
            warning('Error processing %s: %s', fName, ME.message);
        end
    end
    
    fprintf('\nAll graphs processed successfully!\n');
end

function parsave(filename, x, isDirected)
    directed = isDirected;
    save(filename, 'x', 'directed', '-v7.3');
end

