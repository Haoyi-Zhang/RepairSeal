"""Semantic checking diagrams and paired process measurements for RepairSeal."""
import json
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from pictograms import icon

from figure_style import (AMBER, BLUE, LIGHT, MINT, MUTED, RULE, SAND, TEAL, Plate,
                          arguments, grid, paper_style, plot, plt, save)

HERE=Path(__file__).resolve().parent

def checks(d,x,y,rows=3,cols=3,edge=BLUE,fill=LIGHT):
    for i in range(rows):
        for j in range(cols):
            d.frame(x+8*j,y-7*i,5.6,4.6,fill,edge)

def status(d,x,y,yes,tone):
    d.dot(x,y,'',edge=tone,r=9,fill=MINT if yes else SAND)
    xx,yy=([x-4,x-1,x+5],[y,y-3,y+4]) if yes else ([x-4,x+4],[y,y])
    d.ax.plot(xx,yy,color=tone,lw=1.05,solid_capstyle='round',zorder=6)

def boundary(out,preview):
    from diagram_ink import emit
    emit('checking-boundary',out,preview)

def receiver(out,preview):
    from diagram_ink import emit
    emit('trust-boundary',out,preview)

def obligations(out,preview):
    result=json.loads((HERE/'../results/upstream-ceil/summary.json').read_text(encoding='utf8'))
    cases={r['variant']:r for r in result['cases']}
    U=2**32-1
    pairs={tuple(o['input']) for o in cases['supplied']['observations']}
    ms,ns=map(sorted,map(set,zip(*pairs)))
    assert len(ms)*len(ns)==len(pairs)==42
    repaired={(m,n) for m,n in pairs if m>U-(n-1)}
    assert len(repaired)==result['repair_points']==12
    assert len(pairs-repaired)==result['preserve_points']==30
    a=cases['original']['witness']; b=cases['regression']['witness']
    assert (tuple(a['input']),a['obligation'])==((2,U),'repair')
    assert (tuple(b['input']),b['obligation'])==((0,1),'preserve')
    assert cases['supplied']['status']=='ACCEPT'
    d=Plate(426,112)
    d.head(8,102,'(a) Input grid')
    d.head(228,102,'(b) Obligation by region')
    d.rule(215,10,215,103)
    d.text(20,52,r'$n$',8.2)
    d.text(123,88,r'$m$',8.2)
    label=lambda x: r'$U$' if x==U else (r'$U-1$' if x==U-1 else str(x))
    for j,m in enumerate(ms):
        d.text(55+j*23,77,label(m),8)
    for i,n in enumerate(ns):
        y=65-i*10
        d.text(38,y,label(n),8)
        for j,m in enumerate(ms):
            x=55+j*23
            repair=(m,n) in repaired
            d.frame(x-10,y-4,20,8,SAND if repair else MINT,AMBER if repair else TEAL,
                    dash=repair)
            if [m,n]==a['input']:d.text(x,y,'A',7.8,color=AMBER,weight='bold')
            if [m,n]==b['input']:d.text(x,y,'B',7.8,color=TEAL,weight='bold')
    for y,title,count,target,tone,fill in [(79,'Repair',12,'Reference',AMBER,SAND),
                                         (58,'Preserve',30,'Original',TEAL,MINT)]:
        d.frame(231,y-4.5,14,9,fill,tone,dash=title=='Repair')
        d.text(253,y,f'{title} ({count})',9.3,ha='left')
        d.arrow((315,y),(339,y),color=tone)
        d.text(348,y,target,9.3,ha='left',color=tone)
    d.text(228,34,'A   Original fails at (2, U).',8.8,ha='left',color=AMBER)
    d.text(228,20,'B   Regression fails at (0, 1).',8.8,ha='left',color=TEAL)
    d.save(out,'obligation-regions',preview)

def rss(out,preview):
    from matplotlib.lines import Line2D
    with zipfile.ZipFile(HERE/'../results/vector-rss/replication.zip') as z:
        r=json.loads(z.read('results.json'))
    pairs=r['paired']
    assert len(pairs)==r['summary']['requests']==50 and len(r['raw'])==600
    retained=defaultdict(dict)
    for row in r['raw']:
        k=(row['arm'],row['repetition'])
        assert k not in retained[row['request']]
        retained[row['request']][k]=row
    assert len(retained)==50
    for pair in pairs:
        rr=retained[pair['request']]
        assert len(rr)==12 and len({x['checked_cells'] for x in rr.values()})==1
        assert all(x['outcome']==next(iter(rr.values()))['outcome'] for x in rr.values())
        med={arm:statistics.median(rr[arm,i]['peak_rss_kib'] for i in range(3))
             for arm in ('full-json','direct-full','framed-stream','direct-liveness')}
        assert med==pair['median_peak_rss_kib']
        assert pair['stream_to_full']==med['framed-stream']/med['full-json']
        assert pair['live_to_direct']==med['direct-liveness']/med['direct-full']
        assert pair['stream_to_matched_direct']==med['framed-stream']/med['direct-liveness']
    cols=['stream_to_full','live_to_direct','stream_to_matched_direct']
    labels=['Framed / complete JSON','Liveness / full direct','Framed / liveness direct']
    medkeys=['median_stream_to_full','median_live_to_direct','median_stream_to_matched_direct']
    f,a=plot(426,142,left=129,bottom=32,top=26,right=17)
    for i,(k,mkey) in enumerate(zip(cols,medkeys)):
        v=sorted((p[k]-1)*100 for p in pairs)
        assert abs(statistics.median(v)-(r['summary'][mkey]-1)*100)<1e-9
        y=2-i
        a.vlines(v,y+.13,y+.32,color=BLUE,linewidth=.68,alpha=.84,zorder=2)
        lo,_,hi=statistics.quantiles(v,n=4,method='inclusive')
        a.hlines(y-.11,lo,hi,color=BLUE,linewidth=1.15,zorder=3)
        a.scatter(statistics.median(v),y-.11,marker='D',s=25,c=AMBER,zorder=4,
                  edgecolors='white',linewidths=.5)
    a.axvline(0,color=MUTED,lw=.85,ls='--')
    a.set(yticks=[2,1,0],yticklabels=labels,ylim=(-.48,2.48),xlabel='Peak RSS change vs. each row’s baseline (%)')
    keys=[
        Line2D([],[],color=BLUE,marker='|',markersize=7,linestyle='none',label='Request'),
        Line2D([],[],color=BLUE,lw=1.15,label='Middle 50%'),
        Line2D([],[],color=AMBER,marker='D',markersize=4,linestyle='none',label='Median'),
        Line2D([],[],color=MUTED,lw=.85,ls='--',label='0% parity'),
    ]
    a.legend(handles=keys,ncol=4,loc='lower left',bbox_to_anchor=(0,1.025),
             fontsize=8.8,handlelength=1.4,handletextpad=.45,columnspacing=.9,borderaxespad=0)
    a.tick_params(labelsize=9)
    a.tick_params(axis='y',length=0)
    grid(a,'x')
    save(f,out,'rss-replication',preview)

def residency(out,preview):
    summary=json.loads((HERE/'../results/vector-stream.json').read_text(encoding='utf8'))
    rows=summary['rows']
    assert len(rows)==len({r['request'] for r in rows})==380
    assert {r['points'] for r in rows}=={81}
    assert sum(r['checked_cells_per_arm'] for r in rows)==1179684
    ratio=[r['peak_live_vectors_per_streaming_arm']/r['nodes'] for r in rows]
    assert statistics.median(ratio)==summary['median_live_to_all_vectors']==.4
    import numpy as np
    from matplotlib.colors import LogNorm, ListedColormap
    fig=plt.figure(figsize=(426/72,169/72))
    axes=[fig.add_axes([x,.31,w,.49]) for x,w in ((.108,.23),(.385,.23),(.716,.23))]
    for i,(a, (cohort,n)) in enumerate(zip(axes, [('fixture',80),('stress',300)])):
        pts=Counter((r['nodes'],r['peak_live_vectors_per_streaming_arm']) for r in rows if r['population']==cohort)
        assert sum(pts.values())==n
        assert all(18<=x<=54 and 7<=y<=20 for x,y in pts)
        mat=np.array([[pts[x,y] for x in range(18,55)] for y in range(7,21)])
        norm=LogNorm(vmin=1,vmax=max(Counter((r['population'],r['nodes'],r['peak_live_vectors_per_streaming_arm'])
                                             for r in rows).values()))
        # Rectangles mark occupied integer coordinates; blank means zero.
        cmap=ListedColormap(plt.get_cmap('Blues')(np.linspace(.26,1,128)))
        heat=a.pcolormesh(np.arange(17.5,55.5),np.arange(6.5,21.5),np.ma.masked_equal(mat,0),
                          cmap=cmap,norm=norm,edgecolors='none')
        a.set(xlim=(17.5,54.5),ylim=(6.5,20.5),xticks=(20,35,50),yticks=(8,12,16,20))
        a.set_title(f"({chr(97+i)}) {cohort.title()} ({n})",loc='left',pad=5,fontsize=10.4)
        a.tick_params(labelsize=9.2)
        if i==0:a.set_ylabel('Peak live vectors',fontsize=9.5)
        else:a.tick_params(labelleft=False,left=False)
    cax=fig.add_axes([.405,.108,.20,.028])
    ticks=[k for k in (1,2,5,10,20,50,100) if k<=norm.vmax and k in (1,5,20,100)]
    cb=fig.colorbar(heat,cax=cax,orientation='horizontal',ticks=ticks)
    cb.solids.set_rasterized(False)
    cb.ax.minorticks_off()
    cb.ax.tick_params(pad=1.7)
    cb.ax.set_xticklabels([str(k) for k in ticks],fontsize=9)
    fig.text(.112,.108,'Requests per cell',fontsize=9.2)
    fig.text(.36,.152,'All vectors ($N$)',ha='center',fontsize=9.3)
    b=axes[2]
    vals=Counter(ratio)
    xs=sorted(vals)
    assert .18<=xs[0]<=xs[-1]<=.82
    total=0
    ys=[]
    for x in xs:
        total+=vals[x]
        ys.append(100*total/len(rows))
    b.step([.18,*xs,.82],[0,*ys,100],where='post',color=TEAL,lw=.72)
    b.axvline(.4,color=AMBER,ls='--',lw=.55)
    b.set(xlim=(.18,.82),ylim=(-3,103),xticks=(.2,.4,.6,.8),yticks=(0,50,100),
          xlabel='Peak live / all vectors',ylabel='Cumulative (%)')
    b.set_title('(c) Pooled distribution',loc='left',pad=5,fontsize=10.4)
    b.tick_params(labelsize=9.2)
    b.annotate('Median 0.40',(.45,24),fontsize=9.1,color=AMBER)
    grid(b);save(fig,out,'vector-residency',preview)

def diagnostic_order(out,preview):
    from diagram_ink import emit
    emit('diagnostic-order',out,preview)


if __name__=='__main__':
    args=arguments();paper_style()
    for draw in (boundary,receiver,obligations,rss,residency,diagnostic_order):draw(args.outdir,args.previews)
    from diagram_ink import emit_supplemental
    emit_supplemental(args.outdir,args.previews)
