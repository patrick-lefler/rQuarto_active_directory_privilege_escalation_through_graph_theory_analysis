import csv, random, os
random.seed(42)

# =============================================================================
# 1. NAME POOL
# =============================================================================
first_names = [
    "James","Robert","Michael","William","David","Richard","Joseph","Thomas",
    "Charles","Christopher","Daniel","Matthew","Anthony","Mark","Donald",
    "Steven","Paul","Andrew","Joshua","Kenneth","Mary","Patricia","Jennifer",
    "Linda","Barbara","Susan","Jessica","Sarah","Karen","Lisa","Nancy","Betty",
    "Margaret","Sandra","Ashley","Emily","Dorothy","Kimberly","Carol","Michelle",
    "Carlos","Luis","Antonio","Juan","Miguel","Jose","Rafael","Elena","Sofia",
    "Isabella","Maria","Valentina","Gabriela","Wei","Liang","Hui","Yan","Fang",
    "Jing","Lei","Priya","Anita","Neha","Sunita","Kavita","Ravi","Arjun",
    "Fatima","Aisha","Omar","Hassan","Layla","Tariq","Yasmin","Patrick","Siobhan",
    "Declan","Aoife","Ciara","Brendan","Olga","Dmitri","Natasha","Ivan","Katya",
    "Alexei","Amara","Kwame","Zainab","Kofi","Adaeze","Emeka","Nina","Felix",
    "Clara","Hugo","Ingrid","Lars","Astrid","Sven","Mia","Luca","Giulia","Marco"
]

last_names = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
    "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
    "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson",
    "White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker",
    "Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell",
    "Carter","Roberts","Chen","Wang","Li","Zhang","Liu","Yang","Patel","Shah",
    "Sharma","Kumar","Singh","Mehta","Gupta","O'Brien","Murphy","Kelly","Walsh",
    "Burke","Collins","Ryan","Okafor","Mensah","Diallo","Nwosu","Adeyemi",
    "Asante","Banda","Volkov","Petrov","Sokolov","Novak","Dvorak","Horak",
    "Blum","Hassan","Ahmed","Ali","Khan","Malik","Sheikh","Qureshi","Lindqvist",
    "Bergstrom","Johansson","Eriksson","Andersen","Nielsen","Christensen","Hansen"
]

def make_login(first, last, used):
    base = (first[0] + last).lower()
    base = ''.join(c for c in base if c.isalnum())
    login = base
    counter = 2
    while login in used:
        login = base + str(counter)
        counter += 1
    return login

# Generate unique (first, last) pairs
all_pairs = []
seen_full = set()
attempts = 0
while len(all_pairs) < 200 and attempts < 50000:
    f = random.choice(first_names)
    l = random.choice(last_names)
    full = f + " " + l
    if full not in seen_full:
        seen_full.add(full)
        all_pairs.append((f, l))
    attempts += 1

# =============================================================================
# 2. DEPARTMENT SPEC
# =============================================================================
dept_spec = [
    # (dept_id, dept_name, ou_name, total, senior_count)
    ("HR",   "Human Resources",      "HR",         5,  1),
    ("FIN",  "Finance",              "Finance",   15,  2),
    ("RD",   "Research & Dev",       "RD",        65,  4),
    ("OPS",  "Operations",           "Operations",10,  2),
    ("ITS",  "IT Support",           "ITSupport", 10,  2),
    ("PRD",  "Product",              "Product",   15,  2),
    ("PMO",  "Project Management",   "PMO",        5,  1),
    ("SAL",  "Sales & Marketing",    "SalesMktg", 20,  2),
    ("RSK",  "Risk",                 "Risk",       5,  4),
    ("LEG",  "Legal & Compliance",   "Legal",      5,  1),
    ("EXEC", "Executive",            "Executive",  5,  4),
]

senior_titles = {
    "EXEC": ["Chief Financial Officer","Chief Technology Officer",
             "Chief Operating Officer","Chief Risk Officer","Chief Legal Officer"],
    "RSK":  ["Director of Risk","VP Risk Management","Senior Risk Analyst","Head of Enterprise Risk"],
    "RD":   ["Principal Engineer","Staff Engineer","Engineering Manager","Director of Engineering"],
    "FIN":  ["Finance Director","VP Finance"],
    "ITS":  ["IT Manager","Senior Systems Administrator"],
}
standard_titles = {
    "RD":  ["Software Engineer","Data Scientist","DevOps Engineer",
            "Security Engineer","QA Engineer","ML Engineer"],
    "FIN": ["Financial Analyst","Accountant","Treasury Analyst"],
    "ITS": ["Systems Administrator","Help Desk Analyst","Network Technician","IT Analyst"],
    "SAL": ["Account Executive","Marketing Analyst","Business Development Rep","Sales Engineer"],
    "RSK": ["Risk Analyst"],
    "LEG": ["Compliance Analyst"],
}

# =============================================================================
# 3. GENERATE HUMAN USERS
# =============================================================================
users = []
used_logins = set()
name_idx = 0

for (dept_id, dept_name, ou_name, total, senior_count) in dept_spec:
    for j in range(total):
        fn, ln = all_pairs[name_idx]
        name_idx += 1
        login = make_login(fn, ln, used_logins)
        used_logins.add(login)
        is_senior = (j < senior_count)

        if is_senior:
            pool = senior_titles.get(dept_id, [f"Senior {dept_name} Manager"])
            title = random.choice(pool)
        else:
            pool = standard_titles.get(dept_id, [f"{dept_name} Analyst"])
            title = random.choice(pool)

        users.append({
            "username":         login,
            "first_name":       fn,
            "last_name":        ln,
            "display_name":     f"{fn} {ln}",
            "email":            f"{login}@nexacore.com",
            "department":       dept_name,
            "dept_id":          dept_id,
            "ou":               f"OU={ou_name},OU=Users,DC=nexacore,DC=com",
            "title":            title,
            "user_type":        "human",
            "is_senior":        str(is_senior),
            "enabled":          "TRUE",
            "pwd_never_expires":"FALSE",
            "description":      ""
        })

# =============================================================================
# 4. SERVICE ACCOUNTS
# =============================================================================
svc_defs = [
    ("svc-payments",   "SVC Payments Processing",       "Core payment rail integration — PCI scope"),
    ("svc-reporting",  "SVC Finance Reporting",         "Automated GL export and regulatory reporting"),
    ("svc-backup",     "SVC Backup Agent",              "Veeam backup orchestration — all servers"),
    ("svc-monitoring", "SVC Infrastructure Monitoring", "Datadog agent — read access to all hosts"),
    ("svc-deploy",     "SVC Deployment Pipeline",       "CI/CD pipeline execution account (Jenkins)"),
    ("svc-compliance", "SVC Compliance Scanner",        "Automated control testing and evidence collection"),
    ("svc-api-gateway","SVC API Gateway",               "External API authentication token service"),
    ("svc-dbsync",     "SVC Database Sync",             "Cross-environment DB replication agent"),
    ("svc-auditlog",   "SVC Audit Log Aggregator",      "SIEM log forwarder — all endpoints"),
    ("svc-patching",   "SVC Patch Management",          "WSUS/SCCM automated patching agent"),
    ("svc-idp",        "SVC Identity Provider",         "SAML/OIDC SSO broker service"),
    ("svc-vault",      "SVC Secrets Vault",             "HashiCorp Vault unsealing and renewal"),
    ("svc-scheduler",  "SVC Task Scheduler",            "Enterprise job scheduling — finance batch jobs"),
    ("svc-dlp",        "SVC Data Loss Prevention",      "Endpoint DLP agent and policy enforcement"),
    ("svc-pentest",    "SVC Pentest Automation",        "Legacy vulnerability scan account — retained post-engagement"),
]

for (login, display, desc) in svc_defs:
    users.append({
        "username":         login,
        "first_name":       "",
        "last_name":        "",
        "display_name":     display,
        "email":            f"{login}@nexacore.com",
        "department":       "Service Accounts",
        "dept_id":          "SVC",
        "ou":               "OU=ServiceAccounts,DC=nexacore,DC=com",
        "title":            "Service Account",
        "user_type":        "service",
        "is_senior":        "FALSE",
        "enabled":          "TRUE",
        "pwd_never_expires":"TRUE",
        "description":      desc
    })

# =============================================================================
# 5. GROUPS
# =============================================================================
groups = [
    # (group_name, tier, description, group_type)
    ("Domain-Admins",       1, "Full domain control — highest privilege group",              "security"),
    ("IT-Admins",           2, "Local admin rights on all servers and workstations",         "security"),
    ("Security-Admins",     2, "GPO management, security policy, audit log access",          "security"),
    ("Network-Admins",      2, "Firewall, switch, routing configuration access",             "security"),
    ("Backup-Operators",    2, "Read access to all file shares for backup purposes",         "security"),
    ("DevSecOps-Privileged",2, "Elevated access for DevSecOps pipeline operations",          "security"),
    ("HR-Managers",         3, "Senior HR staff — HRIS admin and payroll access",            "security"),
    ("Finance-Managers",    3, "Finance leads — GL system and treasury access",              "security"),
    ("RD-Leads",            3, "Engineering leads — production deployment rights",           "security"),
    ("Ops-Managers",        3, "Operations managers — logistics platform admin",             "security"),
    ("IT-Senior",           3, "Senior IT staff — elevated helpdesk and server access",      "security"),
    ("Product-Managers",    3, "Product leads — feature flag and release management",        "security"),
    ("PMO-Leads",           3, "Project leads — portfolio system admin access",              "security"),
    ("Sales-Managers",      3, "Sales leads — CRM admin and pricing approval",               "security"),
    ("Risk-Senior",         3, "Risk directors — GRC platform admin",                        "security"),
    ("Legal-Managers",      3, "Legal leads — contract management system admin",             "security"),
    ("Executive-Staff",     3, "Executive team — board portal and sensitive data",           "security"),
    ("HR-Users",            4, "All HR department staff",                                    "distribution"),
    ("Finance-Users",       4, "All Finance department staff",                               "distribution"),
    ("RD-Users",            4, "All R&D department staff",                                   "distribution"),
    ("Ops-Users",           4, "All Operations staff",                                       "distribution"),
    ("IT-Users",            4, "All IT Support staff",                                       "distribution"),
    ("Product-Users",       4, "All Product department staff",                               "distribution"),
    ("PMO-Users",           4, "All PMO staff",                                              "distribution"),
    ("Sales-Users",         4, "All Sales & Marketing staff",                                "distribution"),
    ("Risk-Users",          4, "All Risk department staff",                                  "distribution"),
    ("Legal-Users",         4, "All Legal & Compliance staff",                               "distribution"),
    ("Executive-Users",     4, "All Executive team members",                                 "distribution"),
    ("VPN-Users",           4, "Split-tunnel VPN access — all staff",                        "security"),
    ("Finance-Systems",     4, "Access to core finance platform (Workday, NetSuite)",        "security"),
    ("GRC-Platform",        4, "Access to GRC and risk management tooling",                  "security"),
    ("All-Staff",           4, "Universal distribution group — all employees",               "distribution"),
]

# =============================================================================
# 6. GROUP-TO-GROUP NESTING (memberships edge list)
# =============================================================================
group_nesting = [
    # (member_group, parent_group, misconfiguration, notes)
    ("IT-Admins",           "Domain-Admins",       False, "Standard: IT-Admins have domain admin rights"),
    ("Security-Admins",     "Domain-Admins",       False, "Standard: Security-Admins have domain admin rights"),
    ("Network-Admins",      "IT-Admins",           False, "Network team reports to IT-Admins scope"),
    ("Backup-Operators",    "IT-Admins",           False, "Backup agents require IT-Admin level for VSS"),

    # MISCONFIGURATION 1
    ("Finance-Managers",    "Backup-Operators",    True,
     "Legacy 2019 data export project — Finance-Managers added to Backup-Operators, never removed"),

    # MISCONFIGURATION 2
    ("RD-Leads",            "DevSecOps-Privileged",False, "RD leads need elevated DevSecOps pipeline rights"),
    ("DevSecOps-Privileged","Security-Admins",     True,
     "DevSecOps-Privileged nested into Security-Admins during 2022 audit — scope never reduced"),

    # MISCONFIGURATION 4
    ("IT-Senior",           "Network-Admins",      True,
     "IT-Senior granted Network-Admins during 2023 staffing gap — never revoked"),

    # MISCONFIGURATION 5
    ("Executive-Staff",     "Finance-Managers",    True,
     "Executive-Staff nested into Finance-Managers for board reporting — creates unintended privilege path"),

    # Standard Tier 3 → Tier 4
    ("HR-Managers",     "HR-Users",        False, "Managers included in dept distribution group"),
    ("Finance-Managers","Finance-Users",   False, "Managers included in dept distribution group"),
    ("RD-Leads",        "RD-Users",        False, "Leads included in dept distribution group"),
    ("Ops-Managers",    "Ops-Users",       False, "Managers included in dept distribution group"),
    ("IT-Senior",       "IT-Users",        False, "Senior staff included in dept distribution group"),
    ("Product-Managers","Product-Users",   False, "Managers included in dept distribution group"),
    ("PMO-Leads",       "PMO-Users",       False, "Leads included in dept distribution group"),
    ("Sales-Managers",  "Sales-Users",     False, "Managers included in dept distribution group"),
    ("Risk-Senior",     "Risk-Users",      False, "Senior staff included in dept distribution group"),
    ("Legal-Managers",  "Legal-Users",     False, "Managers included in dept distribution group"),
    ("Executive-Staff", "Executive-Users", False, "Exec staff included in exec distribution group"),

    # All dept groups → All-Staff
    ("HR-Users",        "All-Staff", False, "All HR in all-staff distribution"),
    ("Finance-Users",   "All-Staff", False, "All Finance in all-staff distribution"),
    ("RD-Users",        "All-Staff", False, "All R&D in all-staff distribution"),
    ("Ops-Users",       "All-Staff", False, "All Ops in all-staff distribution"),
    ("IT-Users",        "All-Staff", False, "All IT in all-staff distribution"),
    ("Product-Users",   "All-Staff", False, "All Product in all-staff distribution"),
    ("PMO-Users",       "All-Staff", False, "All PMO in all-staff distribution"),
    ("Sales-Users",     "All-Staff", False, "All Sales in all-staff distribution"),
    ("Risk-Users",      "All-Staff", False, "All Risk in all-staff distribution"),
    ("Legal-Users",     "All-Staff", False, "All Legal in all-staff distribution"),
    ("Executive-Users", "All-Staff", False, "All Exec in all-staff distribution"),

    # Resource groups
    ("Finance-Users",   "Finance-Systems", False, "All finance staff get finance platform access"),
    ("Finance-Managers","Finance-Systems", False, "Finance managers also in Finance-Systems"),
    ("Risk-Users",      "GRC-Platform",    False, "Risk staff access GRC tooling"),
    ("Legal-Users",     "GRC-Platform",    False, "Legal staff access GRC tooling"),
    ("All-Staff",       "VPN-Users",       False, "All staff get VPN access"),
]

# =============================================================================
# 7. USER-TO-GROUP MEMBERSHIPS
# =============================================================================
dept_user_group = {
    "HR":"HR-Users","FIN":"Finance-Users","RD":"RD-Users","OPS":"Ops-Users",
    "ITS":"IT-Users","PRD":"Product-Users","PMO":"PMO-Users","SAL":"Sales-Users",
    "RSK":"Risk-Users","LEG":"Legal-Users","EXEC":"Executive-Users"
}
dept_mgr_group = {
    "HR":"HR-Managers","FIN":"Finance-Managers","RD":"RD-Leads","OPS":"Ops-Managers",
    "ITS":"IT-Senior","PRD":"Product-Managers","PMO":"PMO-Leads","SAL":"Sales-Managers",
    "RSK":"Risk-Senior","LEG":"Legal-Managers","EXEC":"Executive-Staff"
}

memberships = []

def add_mem(member, mtype, group, misc=False, notes=""):
    memberships.append({
        "member_name":      member,
        "member_type":      mtype,
        "group_name":       group,
        "misconfiguration": str(misc),
        "notes":            notes
    })

for u in users:
    d = u["dept_id"]
    sr = u["is_senior"] == "True"

    if u["user_type"] == "human":
        if d in dept_user_group:
            add_mem(u["username"], "user", dept_user_group[d])
        if sr and d in dept_mgr_group:
            add_mem(u["username"], "user", dept_mgr_group[d])
        if d == "FIN":
            add_mem(u["username"], "user", "Finance-Systems")
        if d in ("RSK","LEG"):
            add_mem(u["username"], "user", "GRC-Platform")

    else:  # service accounts
        svc = u["username"]
        svc_memberships = {
            "svc-payments":   [("Finance-Systems", False, "")],
            "svc-reporting":  [("IT-Admins", True,
                "svc-reporting granted IT-Admins at deployment for file share write access — dedicated group never created")],
            "svc-backup":     [("Backup-Operators", False, "")],
            "svc-monitoring": [("IT-Users", False, "")],
            "svc-deploy":     [("DevSecOps-Privileged", False, "")],
            "svc-compliance": [("GRC-Platform", False, "")],
            "svc-api-gateway":[("IT-Users", False, "")],
            "svc-dbsync":     [("IT-Admins", False, "")],
            "svc-auditlog":   [("IT-Users", False, "")],
            "svc-patching":   [("IT-Admins", False, "")],
            "svc-idp":        [("IT-Admins", False, "")],
            "svc-vault":      [("Security-Admins", False, "")],
            "svc-scheduler":  [("Finance-Systems", False, "")],
            "svc-dlp":        [("Security-Admins", False, "")],
            "svc-pentest":    [("Network-Admins", True,
                "svc-pentest retained in Network-Admins after external pentest engagement concluded — never deprovisioned")],
        }
        for (grp, misc, notes) in svc_memberships.get(svc, []):
            add_mem(svc, "service", grp, misc, notes)

# Add group-to-group nesting to memberships
for (mg, pg, misc, notes) in group_nesting:
    add_mem(mg, "group", pg, misc, notes)

# =============================================================================
# 8. OU STRUCTURE
# =============================================================================
ou_structure = [
    ("DC=nexacore,DC=com",                              "NexaCore root domain"),
    ("OU=Users,DC=nexacore,DC=com",                     "All human user accounts"),
    ("OU=HR,OU=Users,DC=nexacore,DC=com",               "Human Resources"),
    ("OU=Finance,OU=Users,DC=nexacore,DC=com",          "Finance"),
    ("OU=RD,OU=Users,DC=nexacore,DC=com",               "Research & Development"),
    ("OU=Operations,OU=Users,DC=nexacore,DC=com",       "Operations & Delivery"),
    ("OU=ITSupport,OU=Users,DC=nexacore,DC=com",        "IT Support"),
    ("OU=Product,OU=Users,DC=nexacore,DC=com",          "Product"),
    ("OU=PMO,OU=Users,DC=nexacore,DC=com",              "Project Management Office"),
    ("OU=SalesMktg,OU=Users,DC=nexacore,DC=com",        "Sales & Marketing"),
    ("OU=Risk,OU=Users,DC=nexacore,DC=com",             "Risk"),
    ("OU=Legal,OU=Users,DC=nexacore,DC=com",            "Legal & Compliance"),
    ("OU=Executive,OU=Users,DC=nexacore,DC=com",        "Executive Team"),
    ("OU=ServiceAccounts,DC=nexacore,DC=com",           "Non-interactive service accounts"),
    ("OU=Groups,DC=nexacore,DC=com",                    "Security and distribution groups"),
    ("OU=Computers,DC=nexacore,DC=com",                 "Workstations and servers (placeholder)"),
]

# =============================================================================
# 9. WRITE CSVs
# =============================================================================
os.makedirs("/home/claude/nexacore_ad", exist_ok=True)

def write_csv_file(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

write_csv_file("/home/claude/nexacore_ad/users.csv", users,
    ["username","first_name","last_name","display_name","email",
     "department","dept_id","ou","title","user_type","is_senior",
     "enabled","pwd_never_expires","description"])

write_csv_file("/home/claude/nexacore_ad/groups.csv",
    [{"group_name":g,"tier":t,"description":d,"group_type":gt} for g,t,d,gt in groups],
    ["group_name","tier","description","group_type"])

write_csv_file("/home/claude/nexacore_ad/memberships.csv", memberships,
    ["member_name","member_type","group_name","misconfiguration","notes"])

write_csv_file("/home/claude/nexacore_ad/group_nesting.csv",
    [{"member_group":mg,"parent_group":pg,"misconfiguration":str(mc),"notes":n}
     for mg,pg,mc,n in group_nesting],
    ["member_group","parent_group","misconfiguration","notes"])

write_csv_file("/home/claude/nexacore_ad/ou_structure.csv",
    [{"ou_path":p,"description":d} for p,d in ou_structure],
    ["ou_path","description"])

# =============================================================================
# 10. SUMMARY
# =============================================================================
n_human   = sum(1 for u in users if u["user_type"]=="human")
n_service = sum(1 for u in users if u["user_type"]=="service")
n_misc    = sum(1 for m in memberships if m["misconfiguration"]=="True")

print(f"\n=== NexaCore AD Generation Complete ===")
print(f"Users:            {len(users)}")
print(f"  Human:          {n_human}")
print(f"  Service:        {n_service}")
print(f"Groups:           {len(groups)}")
print(f"Memberships:      {len(memberships)}")
print(f"Misconfigurations:{n_misc}")

print("\nDepartment breakdown:")
from collections import defaultdict
dept_counts = defaultdict(lambda: {"senior":0,"standard":0})
for u in users:
    if u["user_type"]=="human":
        d = u["department"]
        if u["is_senior"]=="True":
            dept_counts[d]["senior"] += 1
        else:
            dept_counts[d]["standard"] += 1

print(f"{'Department':<25} {'Senior':>7} {'Standard':>9} {'Total':>7}")
print("-"*52)
for dept, counts in dept_counts.items():
    tot = counts["senior"] + counts["standard"]
    print(f"{dept:<25} {counts['senior']:>7} {counts['standard']:>9} {tot:>7}")

print("\nMisconfiguration edges:")
for m in memberships:
    if m["misconfiguration"]=="True":
        print(f"  {m['member_name']:<22} → {m['group_name']:<22}  [{m['notes'][:60]}...]")
