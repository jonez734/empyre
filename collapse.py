#!/usr/bin/env python

# https://gist.github.com/sirpengi/5045885 2013-feb-27 in oftcphp sirpengi
# @since 20140529
#def collapse(lst):
#    def chunk(lst):
#        ret = [lst[0],]
#        for i in lst[1:]:
#            print("i=%r" % (i))
#            if ord(i) == ord(ret[-1]) + 1:
#                pass
#            else:
#                yield ret
#                ret = []
#            ret.append(i)
#        yield ret
#    chunked = chunk(lst)
#    ranges = ((min(l), max(l)) for l in chunked)
#    return ", ".join("{0}-{1}".format(*l) if l[0] != l[1] else l[0] for l in ranges)

def collapse(buf):
    for b in range(0, len(buf)-1):
        print(buf[b])
    return buf
    
lst = "1245678Q?"
print("lst=%s" % (lst))
print("intended result='1,2,4-8,Q,?'")
print("actual result=%s" % (collapse(lst)))
