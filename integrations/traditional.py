"""Four traditional families vendored from huvan9527-a11y/buy-cs; no API calls or notifications."""

def cross(a,b,i): return i>0 and a[i]>b[i] and a[i-1]<=b[i-1]
def ema(xs, span):
    k=2/(span+1); out=[xs[0]]
    for x in xs[1:]: out.append(x*k+out[-1]*(1-k))
    return out
def sma(xs,p,i): return sum(xs[i-p+1:i+1])/p if i>=p-1 else None
def signal_types(g):
    c=[x["close"] for x in g]; o=[x["open"] for x in g]; h=[x["high"] for x in g]; l=[x["low"] for x in g]; i=len(g)-1
    if i<35: return []
    out=[]
    # MACD double golden cross (standard and fast); KDJ cross is approximated from RSV smoothed values.
    def macd(fast,slow,sig):
        dif=[a-b for a,b in zip(ema(c,fast),ema(c,slow))]; dea=ema(dif,sig)
        k=[]; d=[]
        for j in range(len(c)):
            lo=min(l[max(0,j-8):j+1]); hi=max(h[max(0,j-8):j+1]); r=50 if hi==lo else 100*(c[j]-lo)/(hi-lo)
            k.append(r if j==0 else k[-1]*2/3+r/3); d.append(k[j] if j==0 else d[-1]*2/3+k[j]/3)
        return cross(dif,dea,i) and any(cross(k,d,j) for j in range(max(1,i-2),i+1))
    if macd(12, 26, 9): out.append("双金叉 12/26/9")
    if macd(5, 12, 4): out.append("双金叉 5/12/4")
    # Two MA families: all pairwise crosses within the last 3 bars, final bullish ordering.
    def triple(ps):
        ma=[[sma(c,p,j) for j in range(len(c))] for p in ps]
        if any(v is None for v in [ma[0][i],ma[1][i],ma[2][i]]) or not (ma[0][i]>ma[1][i]>ma[2][i]): return False
        return any(ma[0][j] is not None and ma[1][j] is not None and ma[2][j] is not None and ma[0][j]>ma[1][j] and ma[1][j]>ma[2][j] and (j==0 or not (ma[0][j-1]>ma[1][j-1]>ma[2][j-1])) for j in range(max(0,i-2),i+1))
    if triple((5, 12, 21)): out.append("均线合一 MA5/12/21")
    if triple((7, 14, 21)): out.append("均线合一 MA7/14/21")
    body=abs(c[i-1]-o[i-1]); upper=h[i-1]-max(o[i-1],c[i-1])
    if upper>=body and upper>=.01*c[i-1] and c[i]>h[i-1]: out.append("上影吞没")
    # 单针：下影线至少为实体的 20%，并且保留价格占比与上部收盘条件。
    for lag in (2, 3):
        j = i - lag
        if j < 0:
            continue
        needle_body = abs(c[j] - o[j])
        needle_lower = min(o[j], c[j]) - l[j]
        entity_bottom = min(o[j], c[j])
        held = min(l[j + 1:i + 1]) >= entity_bottom
        if (
            needle_lower >= 0.2 * needle_body
            and needle_lower >= 0.02 * c[j]
            and (c[j] - l[j]) / max(h[j] - l[j], 1e-9) >= 0.6
            and held
            and c[i] >= c[j]
        ):
            out.append("单针承接")
            break
    return list(dict.fromkeys(out))

def family_count(types):
    """参数组合分开展示，但同一家族只计一个独立买点。"""
    families = set()
    for name in types:
        if name.startswith("双金叉"):
            families.add("双金叉")
        elif name.startswith("均线合一"):
            families.add("均线合一")
        elif name == "上影吞没":
            families.add("上影吞没")
        elif name == "单针承接":
            families.add("单针承接")
    return len(families)


