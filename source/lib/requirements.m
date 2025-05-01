required = { ...
    'Econometrics Toolbox';
    'Statistics and Machine Learning Toolbox'
};

v = ver;
installed = {v.Name};
missing = setdiff(required, installed);
if ~isempty(missing)
    error('Missing toolboxes: %s', strjoin(missing, ', '));
end
