function [Fixdata,maxfix]=Marking(fmark,dat)

    fixB = fmark(1:2:end)';
    fixE = fmark(2:2:end)';
    fixD = fixE- fixB;
    
    [temptijd,idxtB,idxfixB] = intersect(dat.time,fixB);
    xstart = dat.x(idxtB);
    ystart = dat.y(idxtB);
    
    [temptijd,idxtE,idxfixE] = intersect(dat.time,fixE);
    xend = dat.x(idxtE);
    yend = dat.y(idxtE);
    
    for p = 1:length(idxtB)
        xmean(p,1) = mean(dat.x(idxtB(p):idxtE(p)));
        ymean(p,1) = mean(dat.y(idxtB(p):idxtE(p)));
        
        xsd(p,1) = std(dat.x(idxtB(p):idxtE(p)));
        ysd(p,1) = std(dat.y(idxtB(p):idxtE(p)));
    end
    
    fixnr = [1:length(fixB)]';
    fixlabel    = zeros(size(fixnr));
    
    if size(fixB,2) > 1
        fixB = fixB';
        fixE = fixE';
        fixD = fixD';
    end
    
    Fixdata = [fixnr, fixB, fixE, fixD, xstart, ystart, xend, yend, xmean, xsd, ymean, ysd, fixlabel];
    maxfix   = max(fixnr);

        
        
end