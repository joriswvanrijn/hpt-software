%% fixation detection using data
function [thr2,Fixdata,dat,maxfix,SPdata,maxsp]=DetectFixations(x,y,t,fs)

% read data and determine fixations, here cases can be added for other
% mobile eye trackers, as well as changing the fixation detection algorithm
% by altering the function that now runs on line 423.
   
            % this file reads the exported data file from Pupil Labs and gets time
            % stamp and x and y coordinate
            
            % determine start and end times of each fixation in one vector (odd
            % number start times of fixations even number stop times)
            
            % The line below determines fixations start and stop times since the
            % beginning of the recording. For this detection of fixations the algo-
            % rithm of Hessels et (2019 submitted) is used, but this can be replaced
            % by your own favourite or perhaps more suitable fixation detection algorithm.
            % Important is that this algorithm returns a vector that has fixation
            % start times at the odd and fixation end times at the even positions
            % of it.
            
    disp('Determining fixations...');
%% gv.fmark = fixdetectmovingwindow(gv.datx,gv.daty,gv.datt,gv);

%%%--%%% DATA FROM PUPIL LABS   
dat.x = x;
dat.y = y;
dat.time = t;

%%%%% eye tracker defaults

        f.thr           = 5000;     % set very high
        f.counter       = 200;
        f.minfix        = 0.060;       % s
        f.maxgap        = 0.060;        % s
        f.lambda        = 4;        % lambda rel treshhold in sds
        f.windowlength  = 3;     % s moving window average
        f.sf            = fs;       % sampling freq
        f.windowsize    = round(f.windowlength./(1/f.sf)); % window size in samples
    
%%%%% Make sure there are NaNs where there is data loss (pupillabs uses zero) 
% assuming there is an x, y and time signal
% for example dat.x, dat.y, dat.time
 
%%%%% determine velocity
vx                  = detvel(dat.x,dat.time);
vy                  = detvel(dat.y,dat.time);
dat.v               = pythagoras(vx,vy);


%%%%%% determine dispersion

d=sqrt(diff(dat.x).^2+diff(dat.y).^2);


%% Variable velocity threshold
%%%% detect fixations with moving window averaged threshold
max windowstart
maxwinstart = numel(dat.time)-f.windowsize+1;
    
for b=1:maxwinstart
    %tempt   = dat.time(b:b+f.windowsize-1); % get time
    clear mvel
    mvel   = dat.v(b:b+f.windowsize-1); % get vel
    
    %% get fixation-classification threshold
    
    % cleaned up on
    % 16 october 2011 IH

    thr             = f.thr;
    counter         = f.counter;
    minfix          = f.minfix;                        % minfix in ms (verwachting: sec)



    qvel            = mvel < thr;                      % look for velocity below threshold
    qnotnan         = ~isnan(mvel);
    qall            = qnotnan & qvel;
    meanvel         = mean(mvel(qall));                % determine the velocity mean during fixations
    stdvel          = std(mvel(qall));                 % determine the velocity std during fixations

    counter         = 0;
    oldthr          = 0;
    while 1,
        thr2        = meanvel + f.lambda*stdvel;
        qvel        = mvel < thr2;                     % look for velocity below threshold
        
        if round(thr2) == round(oldthr) | counter == f.counter, % f.counter for maximum number of iterations
            break;
        end
        %%%--%%% verwachting: je wilt niet dat twee tresholds achter elkaar hetzelfde zijn?

        meanvel     = mean(mvel(qvel));
        stdvel      = std(mvel(qvel));                 % determine the velocity std during fixations    
        oldthr      = thr2;
        counter     = counter + 1;
    end

    thr2            = meanvel + 3*stdvel;              % determine new threshold based on data noise

    % make vector for thr2 of length mvel
    thrfinal        = repmat(thr2,numel(mvel),1);
    %%    


    if b==1
        thr3 = thrfinal;
        ninwin = ones(length(thrfinal),1);
    else
        % append threshod
        thr3(end-length(thrfinal)+2:end) = thr3(end-length(thrfinal)+2:end)+thrfinal(1:end-1);
        thr3 = [thr3; thrfinal(end)];
        % update number of times in win
        ninwin(end-length(thrfinal)+2:end) = ninwin(end-length(thrfinal)+2:end)+1;
        ninwin = [ninwin; 1];
    end
end

%% now get final thr
% thr3 = thr3./ninwin;


%% Detecting fixations and smooth pursuits
clear mvel
clear thr2

thr2=300;
maxthr=700;


mvel=abs(dat.v);

Tw=round(0.060./(1./f.sf)); %%%--%%% window (25)
Td=5; %%%--%%% treshold dispersion
FixMarks=[];

time=dat.time;


minfix          = f.minfix;                        % minfix in ms

qvel            = mvel < thr2;                     % look for velocity below threshold



% qmax            = mvel > maxthr;                   % Look for velocity above max threshold
%  
% qvel            = qmax+qvel;


% Find fixations, smoothpursuit, saccades
for j=Tw:1:size(d)
    dat.Md(j)=sum(abs(d(j-Tw+1:j)));
    if qvel(j)==1 && dat.Md(j) < Td % fixation
        FixMarks(j)=1; 
    elseif qvel(j)==1 && dat.Md(j) >= Td % smooth pursuit
       FixMarks(j)=0;
    else
        FixMarks(j)=4; % saccade
    end
end


% Classify begin of data
if FixMarks(Tw)==4
    FixMarks(1:25)=4;
    
elseif FixMarks(Tw)==1
        FixMarks(1:25)=1;
else
        FixMarks(1:25)=0;
end



 [on,off]        = detectswitches(FixMarks);           % determine start and end of fixations and smooth purstui (everything in between is saccades)



off.Fix              = time(off.Fix);                        % convcert to time
on.Fix             = time(on.Fix);                       % convert to time
off.SP              = time(off.SP);                        % convcert to time
on.SP             = time(on.SP);                       % convert to time



qfix            = off.Fix - on.Fix > minfix;               % look for small fixations       
on.Fix              = on.Fix(qfix);                        % delete fixations smaller than minfix
off.Fix             = off.Fix(qfix);                       % delete fixations smaller than minfix

qsp            = off.SP - on.SP > minfix;               % look for small smooth pursui       
on.SP              = on.SP(qsp);                        % delete smooth pursui smaller than minfix
off.SP             = off.SP(qsp);                       % delete smooth pursui smaller than minfix


% if size(on,1)>0
% qmax            = on(2:end) - off(1:end-1) > f.maxgap;  %look for fixations that take place short after eachother
% qon            = [true(1);qmax];
% qoff            = [qmax;true(1)];
% on              = on(qon);                        % delete fixations following up another fixations with a duration smaller than minfix
% off             = off(qoff);                       
% end

% if size(on.Fix,1)>0
% on(2:end)       = on(2:end);                       % 
% off(1:end-1)    = off(1:end-1);                    % 

fmark           = sort([on.Fix;off.Fix]);                  % sort the markers fixations
SPmark           = sort([on.SP;off.SP]);                  % sort the markers smoothpursuit

%%

[Fixdata,maxfix]=Marking(fmark,dat);
[SPdata,maxsp]=Marking(SPmark,dat);

end        
        
