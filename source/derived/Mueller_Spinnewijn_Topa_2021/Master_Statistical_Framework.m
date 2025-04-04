%%%%%%%%%
%TABLE 5%
%%%%%%%%%
indir  = 'temp/MST2021/MST/STATISTICAL_FRAMEWORK';
temp   = 'temp';
outdir = 'output/derived/bootstrap_census';

unzip('datastore/raw/bootstrap_census/Mueller_Spinnewijn_Topa_2021/orig/MST2021', 'temp')
addpath(indir,temp,outdir)

%% Load estimation results
results   = csvread(sprintf('%s/stat_estimation_results.csv', indir));

% estimations on bootstrapped moments
i=0;
for ibt=[1001:1240]
    i=i+1;
    bootstrap(i,:) = results(ibt*2-1,:);
end

% dispersion parameter for tau is between 0 and 1 (this is imposed in the estimation so negative values do not improve fit)
bootstrap(:,14)=min(max(bootstrap(:,14),0),1); 



%% Table 5: Estimation Results for Statistical Model
iversion=1;

% 200 bootstrap samples
fboot=1;
nboot=200;

% percent explained by selection: 1-(LD/TD) 
x=1-results(:,[59 61])./results(:,[60 62]);
xse =1-bootstrap(fboot:nboot,[59 61])./bootstrap(fboot:nboot,[60 62]);

% redefine sign of theta (consistent with notation in paper)
results(1*2-1,12)=-results(1*2-1,12);

estimates = [results(1+2*(iversion-1),13) 100*x(1+2*(iversion-1),1)];
std = [std([bootstrap(fboot:nboot,13)],[],1) std(100*xse(fboot:nboot,1),[],1)];

repl = [[bootstrap(fboot:nboot,13)], 100*xse(fboot:nboot,1)];

%sqrt(sum((repl(:,1)-mean(repl(:,1))).^2)/199)
%sqrt(sum((repl(:,2)-mean(repl(:,2))).^2)/199)

est_mat = [["SlopeBias";"ShareExplainedBySelection"],estimates',std'];
repl_mat = [[repmat("SlopeBias",200,1);repmat("ShareExplainedBySelection",200,1)],[repl(:,1) (1:200)';repl(:,2) (1:200)']];

filename_est=append(temp,'/est_mat_MST2021.csv');
filename_repl=append(temp,'/repl_mat_MST2021.csv');

writematrix(est_mat,filename_est);
writematrix(repl_mat,filename_repl);



