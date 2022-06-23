%Detecting of saccades

%Calculate the standard deviation of the numeric samples in the
%acceleration variables

%%% OUR NOTES: SD
SD_AccLeftX=std(Leftacc_x_deg, 'omitnan'); 
SD_AccLeftY=std(Leftacc_y_deg, 'omitnan');
SD_AccRightX=std(Rightacc_x_deg, 'omitnan');
SD_AccRightY=std(Rightacc_y_deg, 'omitnan');
SD_VelLeftX=std(Leftvel_x_deg, 'omitnan'); 
SD_VelLeftY=std(Leftvel_y_deg, 'omitnan'); 
SD_VelRightX=std(Rightvel_x_deg, 'omitnan'); 
SD_VelRightY=std(Rightvel_y_deg, 'omitnan'); 
SDAccLeft=std(Leftacc_deg, 'omitnan');
SDAccRight=std(Rightacc_deg, 'omitnan');
SDVelLeft=std(Leftvel_deg, 'omitnan');
SDVelRight=std(Rightvel_deg, 'omitnan');

%%% OUR NOTES: zero matrices 
%Predefine the other variables with matrices of zeroes or a zero
LeftX_appsac=zeros(size(Leftacc_x_deg));
LeftY_appsac=zeros(size(Leftacc_y_deg));
Left_appsac=zeros(size(Leftacc_y_deg));
Left_in_saccade_all=zeros(size(Leftacc_y_deg));
Left_in_saccade_all(isnan(Leftgaze_x(:))==1)=NaN; %write NaN to in_saccade variable in the blinkperiod
Left_in_saccade=zeros(size(Leftacc_y_deg));
Left_in_saccade(isnan(Leftgaze_x(:))==1)=NaN;
RightX_appsac=zeros(size(Leftacc_x_deg));
RightY_appsac=zeros(size(Leftacc_y_deg));
Right_appsac=zeros(size(Leftacc_y_deg));
Right_in_saccade_all=zeros(size(Leftacc_y_deg));
Right_in_saccade_all(isnan(Rightgaze_x(:))==1)=NaN;
Right_in_saccade=zeros(size(Leftacc_y_deg));
Right_in_saccade(isnan(Rightgaze_x(:))==1)=NaN;

%%% OUR NOTES: counters
CountappsacLeft=0;
Appsac_overview_left=zeros(2000,2);
CountappsacRight=0;
Appsac_overview_right=zeros(2000,2);
AS_para_left=zeros(5000,62);
AS_para_right=zeros(5000,62);
Saccades_left=zeros(5000,18);
Saccades_right=zeros(5000,18);
Saccades_left_main=zeros(5000,21);
Saccades_right_main=zeros(5000,21);
NS_left=0;
Maxvel_left=0;
NS_right=0;
Maxvel_right=0;
Firstmaxvel_L=0;
Firstmaxvel_R=0;



%% 
%Determine the approximate saccade interval, if the acceleration is higher
%than 2.576*SD_acc, corresponding to the 99% confidence interval in a
%normal distribution.
for i=1:length(Leftacc_x_deg)
    if abs(Leftacc_x_deg(i))>2.576*SD_AccLeftX 
        LeftX_appsac(i)=1;
    end
    if abs(Leftacc_y_deg(i))>2.576*SD_AccLeftY 
        LeftY_appsac(i)=1;
    end
    %If the value in appsacX OR appsacY variable is 1, assign value 1 to
    %the appsac (total) variable, write the sample number, accX and accY to
    %the 1st, 2nd and 3rd column of the appsac_overview variable
    if LeftX_appsac(i)==1 || LeftY_appsac(i)==1
        Left_appsac(i)=1;
        CountappsacLeft=CountappsacLeft+1;
        Appsac_overview_left(CountappsacLeft,1)=i;
        Appsac_overview_left(CountappsacLeft,2)=Leftacc_x_deg(i);
        Appsac_overview_left(CountappsacLeft,3)=Leftacc_y_deg(i);
    end
    if isnan(Leftgaze_x(i))==1
        Left_appsac(i)=NaN;
    end
    if abs(Rightacc_x_deg(i)) > 2.576*SD_AccRightX %|| abs(Rightvel_x_deg(i))>=2.576*SD_VelRightX
        RightX_appsac(i)=1;
    end
    if abs(Rightacc_y_deg(i)) > 2.576*SD_AccRightY %|| abs(Rightvel_y_deg(i))>=2.576*SD_VelRightY
        RightY_appsac(i)=1;
    end
    if RightX_appsac(i)==1 || RightY_appsac(i)==1
        Right_appsac(i)=1;
        CountappsacRight=CountappsacRight+1;
        Appsac_overview_right(CountappsacRight,1)=i;
        Appsac_overview_right(CountappsacRight,2)=Leftacc_x_deg(i);
        Appsac_overview_right(CountappsacRight,3)=Leftacc_y_deg(i);
    end
    if isnan(Rightgaze_x(i))==1
        Right_appsac(i)=NaN;
    end
end


%% 
%If two approximate saccadic interval are closer than 20 msec, they are
%merged, fill the samples in between with '1'
for i=1:(length(TARGET_X_TARG1)-20/sd)     
    if (Left_appsac(i)-Left_appsac(i+1)==1)
        for k=1:(20/sd)
            if Left_appsac(i+k)==1
                Left_appsac(i:(i+k))=1;
            end
        end
    end
    if (Right_appsac(i)-Right_appsac(i+1)==1)
        for k=1:(20/sd)
            if Right_appsac(i+k)==1
                Right_appsac(i:(i+k))=1;
            end
        end
    end
end
         
%% 
%Detect the approximate saccade intervals in the Left_appsac and Right_appsac variable. 
%and write parameters to the AS_para variable
for i=2:(length(TARGET_X_TARG1)-1) 
    %Start of an interrupted saccade, not taken into account
    if Left_appsac(i)==1 && isnan(Left_appsac(i-1))==1 
        NS_left=NS_left+1;
        AS_para_left(NS_left,1)=0;
    end


    %Start of a saccade interval, make variable Maxvelsac to temporarily store
    %peakvel parameters
    if Left_appsac(i)==1 && Left_appsac(i-1)==0 
        NS_left=NS_left+1;
        AS_para_left(NS_left,1)=i;
        Maxvelsac_left=zeros(5,12);
        Maxvelsac_left(5,:)=[3,8,13,18,23,28,33,38,43,48,53,58];
        %Write the peakvel parameters of the current sample to the first column of
        %Maxvelsac
        Maxvelsac_left(1:4,1)=[Leftvel_deg(i);i;Leftvel_x_deg(i);Leftvel_y_deg(i)];
    end




    %During the saccade, if the velocity is higher than the velocity stored
    %in Maxvelsac, write the new velocity parameters to Maxvelsac
    if Left_appsac(i)==1 && AS_para_left(NS_left,1)~=0
            if  AS_para_left(NS_left,3)==0 && Leftvel_deg(i) > Maxvelsac_left(1,1) 
                Maxvelsac_left(1:4,1)=[Leftvel_deg(i);i;Leftvel_x_deg(i);Leftvel_y_deg(i)];
            end
            %After the velocity peak (if the velocity is decreasing) or at the end
            %of the saccade interval, write the peakvelocity parameters of the
            %first saccade to AS_para (3rd to 6th column), and the main direction
            %of the saccade to the 7th column
            if AS_para_left(NS_left,3)==0 &&... 
                    (Leftvel_deg(i) < Maxvelsac_left(1,1) ||... 
                    (Left_appsac(i)-Left_appsac(i+1))==1)
                AS_para_left(NS_left,3:6)=Maxvelsac_left(1:4,1);
                AS_para_left(NS_left,7)=direction(Leftvel_x_deg(Maxvelsac_left(2,1)),...
                    Leftvel_y_deg(Maxvelsac_left(2,1)));
            end
            %Search for a maximum of 12 PSO's after the first saccade
            for k=2:12
                if AS_para_left(NS_left,Maxvelsac_left(5,k-1))==0 %if there is no previous saccade detected, stop searching for PSO's
                    break
                end
                if AS_para_left(NS_left,Maxvelsac_left(5,k-1))~=0 &&... %if there is a previous saccade detected
                        AS_para_left(NS_left,Maxvelsac_left(5,k))==0 &&... %and not a peakvel already detected for this PSO
                        i>AS_para_left(NS_left,Maxvelsac_left(5,k-1)+1)... %after the sample nr of the previous saccade
                        && Leftvel_deg(i)>Leftvel_deg(i-1) %if the velocity is increasing
                    Maxvelsac_left(1:4,k)=[Leftvel_deg(i);i;Leftvel_x_deg(i);Leftvel_y_deg(i)]; %write the peakvelocity values to corresponding column of Maxvelsac
                end
                %During the PSO, if the velocity is higher than the velocity stored
                %in Maxvelsac, write the new velocity parameters to Maxvelsac
                if Maxvelsac_left(1,k)~=0 && AS_para_left(NS_left,Maxvelsac_left(5,k))==0 &&... 
                        Leftvel_deg(i)>Maxvelsac_left(1,k)
                    Maxvelsac_left(1:4,k)=[Leftvel_deg(i);i;Leftvel_x_deg(i);Leftvel_y_deg(i)];
                end
                %After the velocity peak (if the velocity is decreasing) or at the end
                %of the saccade interval, write the peakvelocity parameters of the
                %PSO to AS_para 
                if Maxvelsac_left(1,k)~=0 && AS_para_left(NS_left,Maxvelsac_left(5,k))==0 &&... 
                        (Leftvel_deg(i)<Maxvelsac_left(1,k) ||... 
                        (Left_appsac(i)-Left_appsac(i+1))==1)
                    AS_para_left(NS_left,Maxvelsac_left(5,k):Maxvelsac_left(5,k)+3)...
                        =Maxvelsac_left(1:4,k);
                    AS_para_left(NS_left,Maxvelsac_left(5,k)+4)=...
                        direction(Leftvel_x_deg(Maxvelsac_left(2,k)),...
                        Leftvel_y_deg(Maxvelsac_left(2,k)));
                end
            end
    end
    %At the end of the saccade interval, write the endtime to the 2nd
    %column of AS_para
    if (Left_appsac(i)-Left_appsac(i+1))==1&&...
            AS_para_left(NS_left,1)~=0     
        AS_para_left(NS_left,2)=i;
    end

    %Same for the right eye
    
    %Start of an interrupted saccade
    if Right_appsac(i)==1 && isnan(Right_appsac(i-1))==1 
        NS_right=NS_right+1;
        AS_para_right(NS_right,1)=0;
    end
    %Start of a saccade, write parameters
    if Right_appsac(i)==1 && Right_appsac(i-1)==0 
        NS_right=NS_right+1;
        AS_para_right(NS_right,1)=i;
        Maxvelsac_right=zeros(5,12);
        Maxvelsac_right(5,:)=[3,8,13,18,23,28,33,38,43,48,53,58];
        Maxvelsac_right(1:4,1)=[Rightvel_deg(i);i;Rightvel_x_deg(i);Rightvel_y_deg(i)];
    end
    %During the saccade
    if Right_appsac(i)==1 && AS_para_right(NS_right,1)~=0
            %Peakvelocity values of first saccade
            if  AS_para_right(NS_right,3)==0 && Rightvel_deg(i) > Maxvelsac_right(1,1) 
                Maxvelsac_right(1:4,1)=[Rightvel_deg(i);i;Rightvel_x_deg(i);Rightvel_y_deg(i)];
            end
            if AS_para_right(NS_right,3)==0 &&... 
                    (Rightvel_deg(i) < Maxvelsac_right(1,1) ||... 
                    (Right_appsac(i)-Right_appsac(i+1))==1)
                AS_para_right(NS_right,3:6)=Maxvelsac_right(1:4,1);
                AS_para_right(NS_right,7)=direction(Rightvel_x_deg(Maxvelsac_right(2,1)),...
                    Rightvel_y_deg(Maxvelsac_right(2,1)));
            end
            %Search for a maximum of 12 PSO's after the first saccade
            for k=2:12
                if AS_para_right(NS_right,Maxvelsac_right(5,k-1))==0 
                    break
                end
                if AS_para_right(NS_right,Maxvelsac_right(5,k-1))~=0 &&... 
                        AS_para_right(NS_right,Maxvelsac_right(5,k))==0 &&... 
                        i>AS_para_right(NS_right,Maxvelsac_right(5,k-1)+1)... 
                        && Rightvel_deg(i)>Rightvel_deg(i-1) 
                    Maxvelsac_right(1:4,k)=[Rightvel_deg(i);i;Rightvel_x_deg(i);Rightvel_y_deg(i)]; 
                end
                if Maxvelsac_right(1,k)~=0 && AS_para_right(NS_right,Maxvelsac_right(5,k))==0 &&... 
                        Rightvel_deg(i)>Maxvelsac_right(1,k)
                    Maxvelsac_right(1:4,k)=[Rightvel_deg(i);i;Rightvel_x_deg(i);Rightvel_y_deg(i)];
                end
                if Maxvelsac_right(1,k)~=0 && AS_para_right(NS_right,Maxvelsac_right(5,k))==0 &&... 
                        (Rightvel_deg(i)<Maxvelsac_right(1,k) ||... 
                        (Right_appsac(i)-Right_appsac(i+1))==1)
                    AS_para_right(NS_right,Maxvelsac_right(5,k):Maxvelsac_right(5,k)+3)...
                        =Maxvelsac_right(1:4,k);
                    AS_para_right(NS_right,Maxvelsac_right(5,k)+4)=...
                        direction(Rightvel_x_deg(Maxvelsac_right(2,k)),...
                        Rightvel_y_deg(Maxvelsac_right(2,k)));
                end
            end
    end
    %End of the saccade
    if (Right_appsac(i)-Right_appsac(i+1))==1&&...
            AS_para_right(NS_right,1)~=0     
        AS_para_right(NS_right,2)=i;
    end
end

%% 
%Remove rows in AS_para with an interupted saccade
AS_para_left((AS_para_left(:,1)==0 | AS_para_left(:,2)==0),:)=[];
AS_para_right((AS_para_right(:,1)==0 | AS_para_right(:,2)==0),:)=[];


%% 
sac=0;
%For every approximate saccade interval, start from the peakvelocities in
%this interval, and go back and forward from these samples, to find the 
%start and end of the saccade, based on changes in direction. Also search 
%for Peakvelocity and Peakacceleration during this process     
for i=1:length(nonzeros(AS_para_left(:,1)))
    %Set sacpart to 9, so the saccade with the first peakvelocity will have
    %value 10
    sacpart=9;
    %Check the different velocity peaks in the saccade interval
    for w=[3,8,13,18,23,28,33,38,43,48,53,58]
        %If there is no velocity peak anymore, stop the loop
        if AS_para_left(i,w)==0
            break
        else
            Maxvel_left=0;
            Maxacc_left=0;
            Maxdec_left=0;
            Tmaxvel_left=0;
            sac=sac+1; %count the saccade interval
            sacpart=sacpart+1; %count the part of the saccade interval (first=value 10)
    % From the peakvelocity in the approximate saccade interval, go back
    % max 500 msec. Determine the sample direction of the current and
    % previous sample (with the 'direction' function, resulting in a value
    % between 0 and 360 degrees)
            for k=AS_para_left(i,w+1):-1:(AS_para_left(i,w+1)-500/sd) 
                Sampdir=direction(Leftvel_x_deg(k),Leftvel_y_deg(k));
                Sampdirmin1=direction(Leftvel_x_deg(k-1),Leftvel_y_deg(k-1));
                %Check if the current velocity is higher than the value stored
                %in the Maxvel variable. If so, replace this value.
                    if Leftvel_deg(k)>Maxvel_left
                        Maxvel_left = Leftvel_deg(k);
                        Tmaxvel_left=k;
                    end
                %Check if the current acceleration (not decelleration) is
                %higher than the value stored in the Maxacc variable. If so,
                %replace this variable.
                    if Leftacc_deg(k)>Maxacc_left 
                        Maxacc_left = Leftacc_deg(k);
                    end
                    if Leftacc_deg(k)<Maxdec_left
                        Maxdec_left = Leftacc_deg(k);
                    end
                %If the current sample is NaN, don't take this saccade into
                %account (interrupted saccade)
                    if isnan(Leftvel_x_deg(k))==1
                        break
                    end
            %If the difference in direction between the current sample and the previous
            %sample is more than 20 degrees per msec, or the difference between the
            %direction of the previous sample and the main direction is
            %more than 60 degrees, or the velocity of the previous sample
            %is less than 5 degr/s, the current sample is the start of the
            %saccade. Write the parameters to AS_para and Saccades
            %variables
                    if Leftvel_deg(k-1)<5||diffangle(Sampdirmin1,AS_para_left(i,w+4))>60 ||...
                            diffangle(Sampdir,Sampdirmin1)> (20*sd)
                        Left_in_saccade_all(k:AS_para_left(i,w+1))=1;
                        Saccades_left(sac,1)=k;
                        Saccades_left(sac,3)=Leftgaze_x(k);
                        Saccades_left(sac,5)=Leftgaze_y(k);
                        break
                    end    
            end
            if Saccades_left(sac,1)==0
                continue
            end
        %Same procedure from the peakvelocity in the forward direction. Instead
        %of the previous sample, compare with the next sample.
            for k=AS_para_left(i,w+1):(AS_para_left(i,w+1)+500/sd)
                Sampdir=direction(Leftvel_x_deg(k),Leftvel_y_deg(k));
                Sampdirplus1=direction(Leftvel_x_deg(k+1),Leftvel_y_deg(k+1));
                    if Leftvel_deg(k)>Maxvel_left
                        Maxvel_left = Leftvel_deg(k);
                        Tmaxvel_left = k;
                    end
                    if Leftacc_deg(k)>Maxacc_left 
                        Maxacc_left = Leftacc_deg(k);
                    end
                    if Leftacc_deg(k)<Maxdec_left
                        Maxdec_left = Leftacc_deg(k);
                    end
                    if isnan(Leftvel_x_deg(k))==1
                        break
                    end
                    if Leftvel_deg(k+1)<5||diffangle(Sampdirplus1,AS_para_left(i,w+4))>60||...
                            diffangle(Sampdir,Sampdirplus1)>(20*sd)
                        Left_in_saccade_all(AS_para_left(i,w+1):k)=1;
                        Saccades_left(sac,2)=k;
                        Saccades_left(sac,4)=Leftgaze_x(k);
                        Saccades_left(sac,6)=Leftgaze_y(k);
                    break
                    end 
            end
            Saccades_left(sac,7)=Tmaxvel_left; 
            Saccades_left(sac,8)=Maxvel_left; 
            Saccades_left(sac,9)=Maxacc_left;
            Saccades_left(sac,10)=Maxdec_left;
            Saccades_left(sac,16)=sacpart;
            Saccades_left(sac,17)=i;
            %If two subsequent saccade interval parts result in the same saccade
            %(peakvelocity is equal), discard the one with the shortest 
            %duration, if equal, the last saccade is discarded
            if sac>1 && Saccades_left(sac,7)==Saccades_left(sac-1,7)
                if Saccades_left(sac,2)-Saccades_left(sac,1)<...
                        Saccades_left(sac-1,2)-Saccades_left(sac-1,1)
                Saccades_left(sac,:)=[];
                sac=sac-1;
                sacpart=sacpart-1;
                elseif Saccades_left(sac,2)-Saccades_left(sac,1)>...
                        Saccades_left(sac-1,2)-Saccades_left(sac-1,1)
                Saccades_left(sac-1,:)=[];
                sac=sac-1;
                sacpart=sacpart-1;
                elseif Saccades_left(sac,2)-Saccades_left(sac,1)==...
                        Saccades_left(sac-1,2)-Saccades_left(sac-1,1)
                Saccades_left(sac,:)=[];
                sac=sac-1;
                sacpart=sacpart-1;
                end
            end
        end
    end
end
 %%
%Same procedure for the right eye
sac=0; 
for i=1:length(nonzeros(AS_para_right(:,1)))
    sacpart=9;
    %Check the different velocity peak in the saccade interval
    for w=[3,8,13,18,23,28,33,38,43,48,53,58]
        if AS_para_right(i,w)==0
            break
        else
            Maxvel_right=0;
            Maxacc_right=0;
            Maxdec_right=0;
            Tmaxvel_right=0;
            sac=sac+1;
            sacpart=sacpart+1;
            %Determine start of saccade
            for k=AS_para_right(i,w+1):-1:(AS_para_right(i,w+1)-500/sd) 
                Sampdir=direction(Rightvel_x_deg(k),Rightvel_y_deg(k));
                Sampdirmin1=direction(Rightvel_x_deg(k-1),Rightvel_y_deg(k-1));
                    if Rightvel_deg(k)>Maxvel_right
                        Maxvel_right = Rightvel_deg(k);
                        Tmaxvel_right=k;
                    end
                    if Rightacc_deg(k)>Maxacc_right 
                        Maxacc_right = Rightacc_deg(k);
                    end
                    if Rightacc_deg(k)<Maxdec_right
                        Maxdec_right = Rightacc_deg(k);
                    end
                    %Interrupted saccade
                    if isnan(Rightvel_x_deg(k))==1
                        break
                    end
                    % Check criteria for start saccade
                    if Rightvel_deg(k-1)<5 ||diffangle(Sampdirmin1,AS_para_right(i,w+4))>60||...
                            diffangle(Sampdir,Sampdirmin1)>20*sd
                        Right_in_saccade_all(k:AS_para_right(i,w+1))=1;
                        Saccades_right(sac,1)=k;
                        Saccades_right(sac,3)=Rightgaze_x(k);
                        Saccades_right(sac,5)=Rightgaze_y(k);
                        break
                    end    
            end
            %if no start is detected, continue with next 
            if Saccades_right(sac,1)==0
                continue
            end
            %Determine end of saccade
            for k=AS_para_right(i,w+1):(AS_para_right(i,w+1)+500/sd)
                Sampdir=direction(Rightvel_x_deg(k),Rightvel_y_deg(k));
                Sampdirplus1=direction(Rightvel_x_deg(k+1),Rightvel_y_deg(k+1));
                    if Rightvel_deg(k)>Maxvel_right
                        Maxvel_right = Rightvel_deg(k);
                        Tmaxvel_right = k;
                    end
                    if Rightacc_deg(k)>Maxacc_right 
                        Maxacc_right = Rightacc_deg(k);
                    end
                    if Rightacc_deg(k)<Maxdec_right
                        Maxdec_right = Rightacc_deg(k);
                    end
                    %Interrupted saccade
                    if isnan(Rightvel_x_deg(k))==1
                        break
                    end
                    % Check criteria for end saccade
                    if Rightvel_deg(k+1)<5 ||diffangle(Sampdirplus1,AS_para_right(i,w+4))>60||...
                            diffangle(Sampdir,Sampdirplus1)>20*sd
                        Right_in_saccade_all(AS_para_right(i,w+1):k)=1;
                        Saccades_right(sac,2)=k;
                        Saccades_right(sac,4)=Rightgaze_x(k);
                        Saccades_right(sac,6)=Rightgaze_y(k);
                    break
                    end 
            end
            Saccades_right(sac,7)=Tmaxvel_right; 
            Saccades_right(sac,8)=Maxvel_right; 
            Saccades_right(sac,9)=Maxacc_right;
            Saccades_right(sac,10)=Maxdec_right;
            Saccades_right(sac,16)=sacpart; %indicating the nr of the saccade, 
                %in the interval, nr 10 is the first saccade, 11 the
                %second, etc.
           Saccades_right(sac,17)=i;

            %If two saccade parts result in same saccade, one with the
            %shortest duration is discarded
            if sac>1 && Saccades_right(sac,7)==Saccades_right(sac-1,7)
                if Saccades_right(sac,2)-Saccades_right(sac,1)<...
                        Saccades_right(sac-1,2)-Saccades_right(sac-1,1)
                Saccades_right(sac,:)=[];
                sac=sac-1;
                sacpart=sacpart-1;
                elseif Saccades_right(sac,2)-Saccades_right(sac,1)>...
                        Saccades_right(sac-1,2)-Saccades_right(sac-1,1)
                Saccades_right(sac-1,:)=[];
                sac=sac-1;
                sacpart=sacpart-1;
                elseif Saccades_right(sac,2)-Saccades_right(sac,1)==...
                        Saccades_right(sac-1,2)-Saccades_right(sac-1,1)
                Saccades_right(sac,:)=[];
                sac=sac-1;
                sacpart=sacpart-1;
                end
            end
        end
    end
end



%% 
%Calculate the duration, amplitude X, Y and total, and the direction of the
%saccades
for i=1:length((Saccades_left(:,1)))
    if Saccades_left(i,1)~=0
        Saccades_left(i,11)=Saccades_left(i,2)-Saccades_left(i,1)+1;
        Saccades_left(i,12)=pixtodegX(abs(Saccades_left(i,4)-Saccades_left(i,3)),...
            Saccades_left(i,3),Saccades_left(i,5),widthpix,heightpix,widthcm,heightcm,view_dist);
        Saccades_left(i,13)=pixtodegY(abs(Saccades_left(i,6)-Saccades_left(i,5)),...
            Saccades_left(i,3),Saccades_left(i,5),widthpix,heightpix,widthcm,heightcm,view_dist);
        Saccades_left(i,14)=sqrt(Saccades_left(i,12)^2+Saccades_left(i,13)^2);
        Saccades_left(i,15)=direction(Leftvel_x_deg(Saccades_left(i,7)),...
            Leftvel_y_deg(Saccades_left(i,7)));
    end
end

for i=1:length((Saccades_right(:,1))) 
    if Saccades_right(i,1)~=0
        Saccades_right(i,11)=Saccades_right(i,2)-Saccades_right(i,1)+1;
        Saccades_right(i,12)=pixtodegX(abs(Saccades_right(i,4)-Saccades_right(i,3)),...
            Saccades_right(i,3),Saccades_right(i,5),widthpix,heightpix,widthcm,heightcm,view_dist);
        Saccades_right(i,13)=pixtodegY(abs(Saccades_right(i,6)-Saccades_right(i,5)),...
            Saccades_right(i,3),Saccades_right(i,5),widthpix,heightpix,widthcm,heightcm,view_dist);
        Saccades_right(i,14)=sqrt(Saccades_right(i,12)^2+Saccades_right(i,13)^2);
        Saccades_right(i,15)=direction(Rightvel_x_deg(Saccades_right(i,7)),...
            Rightvel_y_deg(Saccades_right(i,7)));
    end
end

%% 
%Write saccades with a minimal duration of 8 msec and minimal amplitude of
%0.15 degree to the new variables Saccades_long
Saccades_left_long=Saccades_left(((Saccades_left(:,11)>=(8/sd))&(Saccades_left(:,14)>=0.15)),:);
Saccades_right_long=Saccades_right(((Saccades_right(:,11)>=(8/sd))&(Saccades_right(:,14)>=0.15)),:);

for i=1:length(Saccades_left_long(:,1))
    Left_in_saccade(Saccades_left_long(i,1):Saccades_left_long(i,2))=1;
end
for i=1:length(Saccades_right_long(:,1))
    Right_in_saccade(Saccades_right_long(i,1):Saccades_right_long(i,2))=1;
end
%%
%Check the different saccades (incl PSO's) detected in one saccade
%interval. The saccade with the highest peakvelocity is considered as the
%main saccade, and written to the new variable Saccades_main
mainsac=0;
for i=1:length(Saccades_left_long(:,1))
    %if only one saccade is detected in an interval, 
    %(the time inbetween the saccades is more than 20 msec)
    %write the parameters of this saccade to Saccades_main, and give value
    %10 to this saccades in the 17th column of saccades_long
    if (i==1 || Saccades_left_long(i,1)-Saccades_left_long(i-1,2)>=20/sd)&&... 
        (i==length(Saccades_left_long(:,1)) ||...
            Saccades_left_long(i+1,1)-Saccades_left_long(i,2)>=20/sd)           
        mainsac=mainsac+1;
        Saccades_left_main(mainsac,1:16)=Saccades_left_long(i,1:16);
        Saccades_left_long(i,17)=10;
    %if there is more than one saccade after this saccade, in the same 
    %saccade complex (time inbetween saccades is <20 msec),
    %first check how many parts of the saccade complex are detected, 
    %write this number to pso variable
    elseif (i==1 || Saccades_left_long(i,1)-Saccades_left_long(i-1,2)>=20/sd)&&...
        Saccades_left_long(i+1,1)-Saccades_left_long(i,2)<20/sd
        pso=1;
        for k=2:6
            if (i+k)>length(Saccades_left_long(:,1)) ||... 
                    Saccades_left_long(i+k,1)-Saccades_left_long(i+k-1,2)>=20/sd
                break
            elseif Saccades_left_long(i+k,1)-Saccades_left_long(i+k-1,2)<20/sd
                pso=pso+1;
            end
        end
        %Take the saccade with the highest peakvelocity as the main saccade
        Row_sacmaxvel=find(Saccades_left_long(:,8)==(max(Saccades_left_long(i:i+pso,8))),1);
        mainsac=mainsac+1;
        %Write the parameters of this saccades to Saccades_main
        Saccades_left_main(mainsac,1:16)=Saccades_left_long(Row_sacmaxvel,1:16);
        %If this saccade was the first saccade detected in the interval,
        %the value in the 17th column of Saccades_long is copied from the 16th column
        if Saccades_left_long(Row_sacmaxvel,16)==10
            Saccades_left_long(i:i+pso,17)=Saccades_left_long(i:i+pso,16);
        %if this saccade was not the first saccade in the interval, reduce
        %the value of the 16th column to the 17th column, resulting in value 10 
        %in the 17th column for the main saccade (value <10 for a saccade
        %before the main saccade, and value >10 for one after)
        elseif Saccades_left_long(Row_sacmaxvel,16)~=10
            Saccades_left_long(i:i+pso,17)=Saccades_left_long(i:i+pso,16)-(Saccades_left_long(Row_sacmaxvel,16)-10);
        end
    end        
end
%Same for the right eye
mainsac=0;
for i=1:length(Saccades_right_long(:,1))
    %only one saccade detected 
    if (i==1 || Saccades_right_long(i,1)-Saccades_right_long(i-1,2)>=20/sd)&&... 
        (i==length(Saccades_right_long(:,1)) ||...
            Saccades_right_long(i+1,1)-Saccades_right_long(i,2)>=20/sd) 
        mainsac=mainsac+1;
        Saccades_right_main(mainsac,1:16)=Saccades_right_long(i,1:16);
        Saccades_right_long(i,17)=10;               
    %more than one saccade detected 
    elseif (i==1 || Saccades_right_long(i,1)-Saccades_right_long(i-1,2)>=20/sd)&&...
        Saccades_right_long(i+1,1)-Saccades_right_long(i,2)<20/sd
        pso=1;
        for k=2:6
            if (i+k)>length(Saccades_right_long(:,1)) ||...
                    Saccades_right_long(i+k,1)-Saccades_right_long(i+k-1,2)>=20/sd
                break
            elseif Saccades_right_long(i+k,1)-Saccades_right_long(i+k-1,2)<20/sd
                pso=pso+1;
            end
        end
        %Take the saccade with the highest peakvelocity as the main saccade
        Row_sacmaxvel=find(Saccades_right_long(:,8)==(max(Saccades_right_long(i:i+pso,8))),1);
        mainsac=mainsac+1;
        Saccades_right_main(mainsac,1:16)=Saccades_right_long(Row_sacmaxvel,1:16);
        %First saccade in the interval
        if Saccades_right_long(Row_sacmaxvel,16)==10
            Saccades_right_long(i:i+pso,17)=Saccades_right_long(i:i+pso,16);
        %Not the first saccade in the interval
        elseif Saccades_right_long(Row_sacmaxvel,16)~=10
            Saccades_right_long(i:i+pso,17)=Saccades_right_long(i:i+pso,16)-(Saccades_right_long(Row_sacmaxvel,16)-10);
        end
    end        
end

%Display the number of main saccades detected
Nr_mainsac_left=length(nonzeros(Saccades_left_main(:,1)))
Nr_mainsac_right=length(nonzeros(Saccades_right_main(:,1)))