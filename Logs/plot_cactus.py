import glob
import os
import matplotlib.pyplot as plt

plotmarkers = ["H","^","x","+","D","*","o","d","v",">"]
def load_logfile(fn, tl=5000 ):    
    res = list()
    sname = ""
    total = 0
    sat_solved = 0
    unsat_solved =0
    par2 = 0    
    with open(fn,"r") as infile:
        for line in infile:                          
                total = total + 1
                line = line.strip("\r\n ")              
                p = line.split(" ")
                if sname == "":
                    sname = p[0]
                if (float(p[2])>tl):
                    p[3]="INDET"
                if (p[3]!="INDET"):
                    res.append([float(p[2]),p[3]])
                    par2 = par2 + float(p[2])
                    if p[3]=="SAT":
                        sat_solved = sat_solved + 1 
                    if p[3]=="UNSAT":
                        unsat_solved = unsat_solved + 1 
                else:
                    par2 = par2 + tl*2
                        
              #res[p[1]] = [p[0],p[2],p[3]]
    par2norm = par2/total
    return sname,res, sat_solved,unsat_solved,par2,par2norm

def load_logs(pathname, title ="" ,xmin=0, tl = 5000, wide = False, filter=""):
    fn = pathname + pathname.split("/")[-2]+"_cactus_" +str(tl)
    if filter!="":
        fn = fn + "_"+filter
    if wide == True:
        fn = fn + "_wide"
    fn = fn+".pdf"    
    fn_rep = pathname + pathname.split("/")[-2]+"_" +str(tl)+"_report"

    files = glob.glob(pathname+"*log")    
    results = dict()
    max_solved = 0
    for i in range(len(files)):
        u = files[i]
        print(str(u))
        h,v_unfiltered,ss,us,par2,par2norm = load_logfile(u,tl)        
        v=[]
        if filter!="":
            v = [g[0] for g in v_unfiltered if g[1]==filter]
        else:
            v = [g[0] for g in v_unfiltered]
        v = sorted(v)            
        for u in range(len(v)):            
            if v[u]>tl:
                v[u]=2*tl
        cur_solved = len(v)
        for u in range(len(v)):            
            if v[u] > tl:
                cur_solved = u                
                break
                
        if cur_solved > max_solved:
            max_solved = cur_solved
                
        results[i] = [h,v,cur_solved,par2,par2norm, ss,us]
        
        ind = len(results)-1
        if (ind > 0):
            while (ind>0):                
                if (results[i][2] > results[ind-1][2]) or ((results[i][2] == results[ind-1][2]) and (results[i][3]<results[ind-1][3])):
                    ind = ind - 1
                else:
                    break
            if ind != i:
                j = i
                while j>ind:
                    results[j]=results[j-1]
                    j = j-1                
                results[ind] = [h,v,cur_solved,par2,par2norm,ss,us]       
                        
    if (filter == ""):
        report = list()
        report.append(["Solver","SCR","PAR2", "PAR2-norm","SAT","UNSAT"])
        for u in range(len(results)):            
            report.append([results[u][0],str(results[u][2]),str(results[u][3]),str(results[u][4]),str(results[u][5]),str(results[u][6])])
        #print(report)
        cols = [0]*6
        
        for u in range(len(report)):            
            for h in range(6):
                if cols[h]<len(report[u][h]):
                    cols[h] = len(report[u][h])+3
        
        for u in range(len(report)):            
            for h in range(6):
                if len(report[u][h])<cols[h]:
                    report[u][h]=" "*(cols[h]-len(report[u][h]))+report[u][h]

        with open(fn_rep,"w") as outfile:        
            for u in range(len(report)):            
                outfile.write(" ".join(report[u])+"\r\n")

    maxlen = 0
    for u in results:
        if maxlen <= len(results[u][1]):
            maxlen = len(results[u][1])+1
    
    for u in results:
        while  len(results[u][1]) < maxlen:
            results[u][1].append(tl*2)
    
    current_figure = ""
    if wide == True:
        current_figure = plt.figure(figsize=(12,5))
    else:
        current_figure = plt.figure(figsize=(10,8))
    
    palette = plt.get_cmap("Set1")
    
    plt.tight_layout()
    
    for u in results:
        #plt.plot(range(0,results[u][2]+1),results[u][1][0:results[u][2]+1],linewidth = 0.7,marker = plotmarkers[u],fillstyle='none', color=palette(u),label=results[u][0])
        plt.plot(range(0,maxlen),results[u][1][0:maxlen],linewidth = 0.7,marker = plotmarkers[u],fillstyle='none', color=palette(u%9),label=results[u][0])
    plt.xlim(xmin,max_solved+10)
    plt.grid(True)
    plt.ylim(0,tl)
    plt.xlabel("Instances")
    plt.ylabel("Time")
    plt.legend(loc=2)
    plt.title(filter)
    plt.savefig(fn)
    #plt.savefig(fn_svg)
    plt.clf()
    plt.close(current_figure)
    #plt.show()

def list_dirs(pathname):
    pathlist = glob.glob(pathname+"*/")
    pathlist = [u.replace("\\","/") for u in pathlist]
    return pathlist
    
current_dir = os.path.dirname(os.path.abspath(__file__))+"/";
pl = list_dirs(current_dir)
for u in pl:
    #print(str(u))
    load_logs(u,"",100,2500)
    load_logs(u,"",100,5000)
    load_logs(u,"",100,5000,True)
    load_logs(u,"",0,5000,True,"UNSAT")
    load_logs(u,"",0,5000,True,"SAT")
    