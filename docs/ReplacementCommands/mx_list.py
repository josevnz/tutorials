#!/usr/bin/env python3
"""
List MX records for a particular domain, using the host resolver settings
kodegeek.com@protonmail.com
"""
import sys
import ldns

if __name__ == "__main__":
    for domain in sys.argv[1:]:
        resolver = ldns.ldns_resolver.new_frm_file("/etc/resolv.conf")
        pkt = resolver.query(domain, ldns.LDNS_RR_TYPE_MX, ldns.LDNS_RR_CLASS_IN)
        if pkt:
            mx = pkt.rr_list_by_type(ldns.LDNS_RR_TYPE_MX, ldns.LDNS_SECTION_ANSWER)
            if mx:
                mx.sort()
                print(f"{mx}")
