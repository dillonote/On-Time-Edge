"""
Manufacturing domain knowledge for the On Time Edge Copy Bot.

Gives the bot deep expertise in production scheduling, supply chain
planning, and manufacturing execution — so it writes copy that sounds
like it came from someone who has actually stood on a shop floor.

Used by consciousness.py and main.py to:
1. Inject domain expertise into LLM system prompts
2. Provide industry-specific pain points for template personalization
3. Supply operational vocabulary and objection responses
"""

from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Scheduling concepts — what the bot must understand
# ---------------------------------------------------------------------------
SCHEDULING_CONCEPTS: Dict[str, str] = {
    "finite_vs_infinite": (
        "Infinite capacity planning (MRP) assumes unlimited resources — it tells you "
        "what to make and when, but ignores whether you actually have the machines, "
        "people, or materials to do it. Finite capacity scheduling (APS) respects real "
        "constraints: machine availability, labor shifts, tooling, material arrival "
        "dates, and setup sequences. The gap between infinite and finite is where "
        "most schedule breaks happen."
    ),
    "forward_vs_backward": (
        "Forward scheduling starts from now and asks 'when can I finish?' — used when "
        "the constraint is capacity. Backward scheduling starts from the due date and "
        "asks 'when must I start?' — used when the constraint is delivery. Most real "
        "plants need both: backward for on-time delivery, forward for feasibility. "
        "The tension between them reveals the true constraint."
    ),
    "theory_of_constraints": (
        "Eli Goldratt's TOC: every system has one binding constraint that limits "
        "throughput. Optimizing anything other than the constraint is waste. The "
        "five focusing steps: Identify → Exploit → Subordinate → Elevate → Repeat. "
        "In scheduling terms: find the bottleneck, maximize its utilization, schedule "
        "everything else around it, and only add capacity when you've exhausted the "
        "current constraint. OTE applies TOC as a core methodology."
    ),
    "drum_buffer_rope": (
        "DBR (Drum-Buffer-Rope): the drum is the constraint resource that sets the "
        "pace. The buffer is time protection before the constraint (not inventory "
        "everywhere). The rope is the release mechanism that prevents overloading "
        "upstream work centers. This prevents the #1 scheduling failure: releasing "
        "too much work to the floor."
    ),
    "setup_optimization": (
        "Setup/changeover time is often the hidden constraint. SMED (Single-Minute "
        "Exchange of Die) reduces it mechanically. APS reduces it algorithmically — "
        "by sequencing similar jobs together (campaign scheduling), optimizing color "
        "sequences (light to dark), grouping compatible materials, and minimizing "
        "tool changes. The best implementations combine both."
    ),
    "batch_lot_sizing": (
        "Lot sizing balances setup cost against inventory cost. Economic Order "
        "Quantity (EOQ) is the textbook answer, but real plants face constraints "
        "EOQ ignores: shelf life, tank sizes, furnace capacity, minimum run lengths, "
        "and customer-specific requirements. APS handles lot sizing as a constraint, "
        "not just a formula."
    ),
    "sequencing_rules": (
        "Common dispatching rules: SPT (shortest processing time — minimizes average "
        "flow time), EDD (earliest due date — minimizes maximum tardiness), CR "
        "(critical ratio — balances urgency), FIFO (first in first out — simple but "
        "suboptimal). No single rule works everywhere. APS evaluates multiple rules "
        "simultaneously against actual constraints and KPIs."
    ),
    "campaign_scheduling": (
        "Running similar products consecutively to minimize changeovers. Critical in "
        "pharma (same API, same equipment train), food (allergen sequencing), plastics "
        "(color families), and metals (alloy grades). The tradeoff: longer campaigns "
        "reduce changeovers but increase inventory and reduce flexibility. The art is "
        "finding the right campaign length for each product family."
    ),
    "constraint_propagation": (
        "When one constraint shifts, it cascades. A delayed material arrival doesn't "
        "just affect one order — it ripples through dependent operations, shared "
        "resources, and downstream customers. Constraint-aware scheduling propagates "
        "these impacts automatically and shows the planner the full picture before "
        "they decide, not after."
    ),
    "what_if_scenarios": (
        "The ability to simulate schedule changes before committing them. 'What if "
        "this machine goes down?' 'What if we expedite this order?' 'What if we add "
        "a Saturday shift?' Without what-if, planners make these decisions blind. "
        "With it, they see downstream impact in seconds — and choose the least-bad "
        "option instead of guessing."
    ),
}

# ---------------------------------------------------------------------------
# Industry-specific pain points
# ---------------------------------------------------------------------------
INDUSTRY_PAIN_POINTS: Dict[str, Dict[str, Any]] = {
    "aerospace": {
        "label": "Aerospace & Defense",
        "pain_points": [
            "Long lead times (months to years) with complex multi-level BOMs",
            "Regulatory compliance (AS9100, ITAR, NADCAP) adds scheduling constraints",
            "MRO (Maintenance, Repair, Overhaul) scheduling with uncertain scope",
            "Engineering changes mid-production disrupt carefully sequenced plans",
            "Capacity sharing across programs with different priority levels",
            "Specialized tooling and fixtures with limited availability",
        ],
        "scheduler_says": (
            "We can't just move things around — every change triggers a paperwork "
            "cascade. And the program managers all think their order is the priority."
        ),
        "vp_says": (
            "Our on-time delivery is killing us on contract renewals. We need "
            "visibility into capacity commitments across programs."
        ),
        "key_metrics": ["OTD to contract milestones", "program margin", "WIP aging"],
    },
    "automotive": {
        "label": "Automotive",
        "pain_points": [
            "JIT/JIS delivery windows measured in hours, not days",
            "Mixed-model assembly lines require precise sequencing",
            "Supplier synchronization across tiers is fragile",
            "Takt time adherence with high product variety",
            "OEM schedule changes with short notice (EDI 830/862)",
            "Penalty clauses for late delivery make every miss expensive",
        ],
        "scheduler_says": (
            "The OEM changes the call-off every week. By the time I replan, "
            "they've changed it again. I'm always chasing yesterday's schedule."
        ),
        "vp_says": (
            "One late shipment and we're on corrective action. We need to stop "
            "being reactive and start seeing problems before they hit the dock."
        ),
        "key_metrics": [
            "PPM (parts per million defects)",
            "OTD to window",
            "takt adherence",
        ],
    },
    "food_beverage": {
        "label": "Food & Beverage",
        "pain_points": [
            "Shelf life and expiration dating constrain production sequences",
            "Allergen changeovers require full CIP (clean-in-place) cycles",
            "Seasonal demand spikes (holidays, harvest) overwhelm capacity",
            "Yield variability from raw material quality fluctuations",
            "Co-packing and private label add scheduling complexity",
            "FSMA/HACCP compliance adds documentation overhead to every batch",
        ],
        "scheduler_says": (
            "I can't just run the most efficient sequence — allergen rules "
            "dictate what follows what. And if product sits too long before "
            "shipping, we scrap it."
        ),
        "vp_says": (
            "We're throwing away product because we can't align production with "
            "actual demand. And the promotional surges crush us every quarter."
        ),
        "key_metrics": [
            "waste/scrap rate",
            "shelf life remaining at ship",
            "fill rate",
        ],
    },
    "pharma": {
        "label": "Pharmaceutical & Life Sciences",
        "pain_points": [
            "GMP compliance means every schedule change needs documentation",
            "Campaign scheduling to minimize cleaning validation between APIs",
            "Equipment qualification/validation constrains what runs where",
            "Batch record requirements add non-productive time to every run",
            "Long lead time raw materials (APIs, excipients) with expiry dates",
            "Multi-site coordination for global supply of regulated products",
        ],
        "scheduler_says": (
            "I can't just move a batch to a different reactor — it's not qualified "
            "for that product. And every campaign break means a 3-day cleaning "
            "validation."
        ),
        "vp_says": (
            "We're sitting on months of WIP waiting for QA release while customers "
            "are on allocation. The disconnect between planning and quality is "
            "killing our service levels."
        ),
        "key_metrics": [
            "batch right-first-time",
            "QA release cycle time",
            "schedule adherence",
        ],
    },
    "medical_device": {
        "label": "Medical Device",
        "pain_points": [
            "FDA 21 CFR Part 820 quality system requirements",
            "Full traceability from raw material through sterilization",
            "Sterilization scheduling (ETO, gamma, autoclave) as a bottleneck",
            "Design changes require revalidation before production",
            "Small lot sizes with high product variety",
            "Demand driven by hospital purchasing cycles and GPO contracts",
        ],
        "scheduler_says": (
            "Sterilization is always the bottleneck. I have product waiting "
            "in queue for days while the autoclave runs someone else's batch."
        ),
        "vp_says": (
            "We need to reduce lead times to compete on GPO contracts, but "
            "compliance requirements make it hard to cut corners anywhere."
        ),
        "key_metrics": [
            "sterilization queue time",
            "lot traceability",
            "OTD to hospital",
        ],
    },
    "metals": {
        "label": "Metals & Metal Parts",
        "pain_points": [
            "Heat/melt scheduling with furnace capacity as the binding constraint",
            "Alloy grade sequencing to minimize contamination between heats",
            "Coil/slab optimization to maximize yield from each melt",
            "Energy cost optimization — run furnaces during off-peak hours",
            "Long cooling times create WIP that blocks downstream operations",
            "Customer-specific chemistry requirements limit batch consolidation",
        ],
        "scheduler_says": (
            "The furnace dictates everything. If I don't sequence the grades "
            "right, I lose hours to transition heats. And downstream is always "
            "waiting on me."
        ),
        "vp_says": (
            "Energy is 30% of our cost. We need to optimize furnace utilization "
            "and run during off-peak windows without sacrificing delivery."
        ),
        "key_metrics": ["furnace utilization", "yield per heat", "energy cost per ton"],
    },
    "cpg": {
        "label": "Consumer Packaged Goods",
        "pain_points": [
            "High-mix, high-volume production with frequent SKU changes",
            "Promotional demand creates unpredictable spikes",
            "Co-packing and contract manufacturing add coordination layers",
            "Packaging line changeovers dominate non-productive time",
            "Retail compliance (OTIF) penalties for late or incomplete shipments",
            "Short product lifecycles mean new introductions are constant",
        ],
        "scheduler_says": (
            "Marketing launches a promo without telling us until the orders "
            "hit. Then it's all-hands to figure out where to fit 3x normal "
            "volume on lines already running flat out."
        ),
        "vp_says": (
            "Walmart's OTIF penalties are eating our margin. We need scheduling "
            "that accounts for promotional lifts before they hit, not after."
        ),
        "key_metrics": [
            "OTIF (on-time in-full)",
            "changeover frequency",
            "SKU fill rate",
        ],
    },
    "plastics": {
        "label": "Plastics & Rubber",
        "pain_points": [
            "Mold changeovers are time-consuming and require skilled technicians",
            "Color sequencing (light to dark) to minimize purge waste",
            "Material drying times create upstream constraints",
            "Multi-cavity molds sharing machines complicate scheduling",
            "Raw material price volatility affects order prioritization",
            "Cycle time variation by material grade and ambient temperature",
        ],
        "scheduler_says": (
            "I spend half my day figuring out color sequences. If I get it "
            "wrong, we burn material on purge and the machine sits idle "
            "waiting for the next setup."
        ),
        "vp_says": (
            "Our machine utilization looks fine on paper, but we're losing "
            "hours every day to changeovers that could be sequenced better."
        ),
        "key_metrics": ["purge waste", "mold utilization", "changeover time"],
    },
}

# ---------------------------------------------------------------------------
# Key manufacturing metrics
# ---------------------------------------------------------------------------
METRICS: Dict[str, str] = {
    "OTD": "On-Time Delivery — percentage of orders shipped by the promised date. The metric customers care about most.",
    "OTIF": "On-Time In-Full — orders delivered on time AND complete. Retail standard (Walmart, Target). Penalties for misses.",
    "OEE": "Overall Equipment Effectiveness = Availability × Performance × Quality. World-class is 85%+. Most plants run 50-65%.",
    "throughput": "Rate of sellable output per unit time. TOC focuses here — it's the only metric that directly generates revenue.",
    "WIP": "Work-In-Process — inventory on the shop floor between operations. Too much = long lead times. Too little = starvation.",
    "cycle_time": "Total time from order release to completion. Includes processing, queue, move, and wait time. Queue time is usually 80%+.",
    "changeover_time": "Time between last good piece of Product A and first good piece of Product B. SMED targets single-digit minutes.",
    "schedule_adherence": "Percentage of planned operations completed as scheduled. Measures execution discipline, not just plan quality.",
    "capacity_utilization": "Actual output ÷ maximum possible output. Misleading in isolation — 100% utilization often means 0% flexibility.",
    "takt_time": "Available production time ÷ customer demand rate. Sets the heartbeat of production. Miss it and you're behind.",
    "lead_time": "Total elapsed time from order to delivery. Includes planning, procurement, production, and shipping. The customer's experience.",
    "fill_rate": "Percentage of demand fulfilled from available stock. Measures supply chain responsiveness.",
    "right_first_time": "Percentage of batches/lots passing quality on the first attempt. Critical in pharma, food, medical device.",
    "inventory_turns": "Annual COGS ÷ average inventory. Higher = leaner. But too high = fragile. Balance matters.",
}

# ---------------------------------------------------------------------------
# Integration patterns — how systems connect
# ---------------------------------------------------------------------------
INTEGRATION_PATTERNS: Dict[str, str] = {
    "isa95_levels": (
        "ISA-95 defines five levels: Level 0-2 (physical process, sensing, control — "
        "SCADA/PLC domain), Level 3 (manufacturing operations — MES/MOM domain), "
        "Level 4 (business planning — ERP/APS domain). Most integration failures "
        "happen at the Level 3-4 boundary: the plan says one thing, the floor does "
        "another, and nobody knows until it's too late."
    ),
    "aps_erp_integration": (
        "APS pulls master data from ERP (BOMs, routings, work centers, calendar, "
        "orders) and pushes back scheduled dates and sequences. Common failures: "
        "stale routing data, missing alternate resources, incorrect setup matrices, "
        "and ERP time buckets too coarse for finite scheduling. The integration must "
        "be bidirectional and near-real-time to stay relevant."
    ),
    "aps_mes_integration": (
        "MES feeds APS with actual production status: what's running, what's done, "
        "what's behind. Without this, APS plans against yesterday's snapshot. Key "
        "data flows: operation completions, scrap/yield actuals, machine status "
        "(up/down/changeover), labor availability. The tighter this loop, the more "
        "the schedule reflects reality."
    ),
    "oee_feedback_loop": (
        "OEE data (availability, performance, quality) feeds back into APS capacity "
        "models. If a machine runs at 72% OEE, scheduling it at 100% capacity "
        "guarantees failure. Smart implementations use rolling OEE to adjust "
        "effective capacity automatically — so the schedule accounts for real "
        "performance, not theoretical."
    ),
    "common_integration_failures": (
        "1) One-way integration (plan pushed but actuals never come back). "
        "2) Batch updates instead of real-time (schedule is always stale). "
        "3) Master data mismatch (ERP routing says 10 min, floor takes 15). "
        "4) No exception handling (system freezes when data is missing). "
        "5) Over-integration (trying to connect everything at once instead of "
        "starting with the critical data flows)."
    ),
}

# ---------------------------------------------------------------------------
# Supply chain planning hierarchy
# ---------------------------------------------------------------------------
PLANNING_HIERARCHY: Dict[str, str] = {
    "strategic": (
        "Network design, facility location, make-vs-buy decisions. Time horizon: "
        "1-5 years. Decisions are expensive to reverse. Tools: network optimization, "
        "scenario modeling. This is where MDIF starts — understanding the strategic "
        "context before touching a single scheduling parameter."
    ),
    "tactical": (
        "S&OP / IBP (Sales & Operations Planning / Integrated Business Planning). "
        "Time horizon: 3-18 months. Balances demand, supply, inventory, and financial "
        "plans. Most companies do S&OP badly — it becomes a monthly slide deck instead "
        "of an actual decision-making process. The output should be a constrained "
        "production plan that APS can execute, not aspirational targets."
    ),
    "operational": (
        "MPS (Master Production Schedule) and MRP (Material Requirements Planning). "
        "Time horizon: weeks to months. MPS sets what to make and when. MRP explodes "
        "BOMs into component and material requirements. The 'nervousness problem': "
        "small demand changes cause massive rescheduling waves. Time fences help — "
        "freezing the near-term schedule while allowing changes further out."
    ),
    "execution": (
        "Detailed finite-capacity scheduling. Time horizon: hours to weeks. This is "
        "where APS lives. Takes MPS/MRP output and creates an executable sequence "
        "that respects real constraints: machine availability, labor, tooling, "
        "materials, setup sequences, and maintenance windows. The gap between "
        "operational planning and execution is where most schedules break."
    ),
    "shop_floor": (
        "Real-time dispatching and execution management (MES domain). Tracks actual "
        "vs planned, captures production data, manages labor assignments. The "
        "schedule is only as good as the floor's ability to execute it — and the "
        "floor's feedback is only useful if it reaches the scheduler in time."
    ),
}

# ---------------------------------------------------------------------------
# Scheduling maturity model
# ---------------------------------------------------------------------------
MATURITY_MODEL: List[Dict[str, str]] = [
    {
        "level": "1 — Tribal Knowledge",
        "description": (
            "Scheduling lives in one person's head. If they're sick, nobody knows "
            "what to run. 'The plan' is a whiteboard or a conversation."
        ),
        "symptoms": "Single point of failure. No visibility. Fire-drill culture.",
        "move_to_next": "Document the current process. Make the implicit explicit.",
    },
    {
        "level": "2 — Spreadsheet Planning",
        "description": (
            "Excel-based scheduling. Better than nothing, but no capacity validation, "
            "no constraint checking, no what-if. The spreadsheet is always out of date "
            "by the time it's printed."
        ),
        "symptoms": "Version control chaos. No real-time updates. Manual rework.",
        "move_to_next": "Acknowledge that Excel was a bridge, not a destination.",
    },
    {
        "level": "3 — Basic MRP/ERP Scheduling",
        "description": (
            "Using ERP's built-in scheduling module. Infinite capacity — assumes you "
            "can make anything anytime. Generates unrealistic dates that the floor "
            "ignores. Planners run MRP then manually adjust in Excel anyway."
        ),
        "symptoms": "MRP dates nobody trusts. Constant expediting. 'We tried scheduling in SAP and it didn't work.'",
        "move_to_next": "Accept that ERP scheduling is a planning tool, not an execution tool. You need finite capacity.",
    },
    {
        "level": "4 — Finite Capacity Scheduling (APS)",
        "description": (
            "Dedicated APS tool with finite capacity, constraint awareness, and "
            "what-if scenarios. Schedule reflects real resource availability. "
            "Planners can see conflicts before they happen."
        ),
        "symptoms": "Schedule is feasible but may not be optimized. Adoption varies by planner.",
        "move_to_next": "Integrate APS with MES for closed-loop feedback. Optimize constraint management.",
    },
    {
        "level": "5 — Constraint-Aware Optimization",
        "description": (
            "APS integrated with MES and OEE. Closed-loop scheduling: actuals feed "
            "back to the plan automatically. What-if scenarios inform decisions. "
            "The constraint is visible, managed, and exploited (TOC)."
        ),
        "symptoms": "Schedule is realistic AND optimized. Cross-plant visibility. Data-driven decisions.",
        "move_to_next": "Add predictive capabilities: AI-driven forecasting, autonomous rescheduling.",
    },
    {
        "level": "6 — Autonomous / Adaptive Scheduling",
        "description": (
            "AI/ML-augmented scheduling. System predicts disruptions (machine failure, "
            "demand changes, supply delays) and proactively adjusts. Human oversight "
            "for exceptions, not routine decisions. This is where MDIF points."
        ),
        "symptoms": "Proactive, not reactive. Continuous optimization. Planners manage exceptions, not the daily schedule.",
        "move_to_next": "You're at the frontier. Continuous improvement and scaling across the enterprise.",
    },
]

# ---------------------------------------------------------------------------
# Common objections with expert-level responses
# ---------------------------------------------------------------------------
OBJECTION_RESPONSES: Dict[str, Dict[str, str]] = {
    "erp_scheduling": {
        "objection": "We already have scheduling in our ERP.",
        "surface_response": (
            "ERP scheduling is infinite capacity — it assumes you can make anything "
            "anytime. That's why your planners export to Excel after MRP runs."
        ),
        "deep_response": (
            "ERP does MRP well: exploding BOMs, netting inventory, generating planned "
            "orders. But it doesn't do finite capacity scheduling. It doesn't know "
            "that Machine A is down for maintenance on Tuesday, or that switching from "
            "Product X to Product Y requires a 4-hour changeover. That's why your "
            "planners spend hours adjusting MRP output manually — they're doing finite "
            "scheduling in their heads. APS makes that explicit and automated."
        ),
    },
    "excel_works": {
        "objection": "Our planners use Excel and it works fine.",
        "surface_response": (
            "It works until the planner is sick, goes on vacation, or the shop floor "
            "changes faster than the spreadsheet can keep up."
        ),
        "deep_response": (
            "Excel is the #1 scheduling tool in manufacturing — and that's the problem. "
            "It has no capacity validation, no constraint checking, no automatic "
            "rescheduling when things change, no audit trail, and no what-if. Your "
            "planner is doing heroic work, but they're doing it blind. APS doesn't "
            "replace the planner — it gives them visibility and speed. The same decision "
            "that takes 2 hours in Excel takes 2 minutes in APS, with full constraint "
            "awareness."
        ),
    },
    "tried_aps_failed": {
        "objection": "We tried APS before and it failed.",
        "surface_response": (
            "Most APS failures are implementation failures, not software failures. "
            "We've seen the patterns across 1000+ sites — and they're fixable."
        ),
        "deep_response": (
            "The top 5 reasons APS implementations fail: 1) Bad master data — garbage "
            "in, garbage out. If your routings and setup matrices are wrong, the "
            "schedule will be wrong. 2) Over-modeling — trying to capture every "
            "constraint on day one instead of starting with the binding constraint. "
            "3) No change management — planners weren't involved in design, so they "
            "don't trust or use the tool. 4) Disconnected from execution — APS "
            "generates a schedule but there's no feedback loop from the floor. "
            "5) Vendor walked away after go-live. We address all five. Our 90-day "
            "methodology starts with the binding constraint, involves planners from "
            "day one, and includes managed services post-go-live."
        ),
    },
    "too_variable": {
        "objection": "Our shop floor is too variable for any plan to stay relevant.",
        "surface_response": (
            "That's exactly the point. A constraint-aware schedule doesn't fight "
            "variability — it accounts for it."
        ),
        "deep_response": (
            "Variability isn't the enemy of scheduling — ignoring variability is. "
            "A static plan fails because it pretends variability doesn't exist. "
            "Constraint-aware scheduling builds variability into the model: buffer "
            "management (TOC), OEE-adjusted capacity, material availability windows, "
            "and real-time feedback from the floor. The schedule isn't a prediction — "
            "it's a decision framework that adapts as reality changes. The question "
            "isn't 'can we make a plan that doesn't change?' It's 'can we make "
            "changes visible and managed instead of chaotic?'"
        ),
    },
    "cant_afford_downtime": {
        "objection": "We can't afford the downtime for implementation.",
        "surface_response": (
            "Our 90-day methodology is designed to run alongside your current process, "
            "not replace it on day one."
        ),
        "deep_response": (
            "We never ask you to stop scheduling. The first phase runs APS in shadow "
            "mode — it generates schedules in parallel with your current process. Your "
            "planners compare outputs, build trust, and identify data issues without "
            "any risk to production. Cutover happens when they're ready, not when the "
            "project plan says so. The 3-day workshop at kickoff aligns everyone on "
            "goals. Engineering starts immediately. First quantifiable results in "
            "~90 days. No big bang."
        ),
    },
    "too_expensive": {
        "objection": "APS is too expensive for our size.",
        "surface_response": (
            "The question isn't what APS costs — it's what bad scheduling costs you "
            "today. Overtime, expediting, missed deliveries, scrap."
        ),
        "deep_response": (
            "Calculate your cost of poor scheduling: overtime hours per week × loaded "
            "labor rate + expedited freight per month + late delivery penalties + "
            "scrap from changeover errors + opportunity cost of lost orders. For most "
            "mid-market manufacturers, that number is 6-10x the annual cost of APS. "
            "We're vendor-agnostic, so we'll recommend the right-sized solution — "
            "not the most expensive one."
        ),
    },
    "planners_wont_use": {
        "objection": "Our planners won't adopt a new system.",
        "surface_response": (
            "That's the #1 reason APS fails — and it's a process problem, not a "
            "software problem. We start with the planners, not despite them."
        ),
        "deep_response": (
            "Adoption fails when the tool is imposed from above without involving "
            "the people who will use it. Our approach: planners participate in the "
            "3-day alignment workshop. They define the constraints. They validate "
            "the model. They run shadow schedules and compare to their current "
            "method. By the time we cut over, they've already proven to themselves "
            "that it works. We also provide ongoing training and managed services — "
            "because adoption is a journey, not a go-live event."
        ),
    },
}

# ---------------------------------------------------------------------------
# APS implementation failure modes
# ---------------------------------------------------------------------------
FAILURE_MODES: List[Dict[str, str]] = [
    {
        "mode": "Bad master data",
        "description": "BOMs, routings, setup matrices, and calendars are wrong or stale.",
        "impact": "Schedule is technically feasible but practically useless.",
        "fix": "Data audit and cleanup as phase 1. Validate against actual floor times.",
    },
    {
        "mode": "Over-modeling",
        "description": "Trying to capture every constraint, exception, and edge case on day one.",
        "impact": "Project stalls in analysis. Model is fragile and unmaintainable.",
        "fix": "Start with the binding constraint only. Add complexity incrementally.",
    },
    {
        "mode": "No change management",
        "description": "Planners excluded from design. Tool imposed from IT or management.",
        "impact": "Planners distrust the schedule and revert to Excel within months.",
        "fix": "Planners participate from day one. Shadow mode before cutover.",
    },
    {
        "mode": "Disconnected from execution",
        "description": "APS generates schedules but gets no feedback from MES or floor.",
        "impact": "Schedule drifts from reality within hours of publication.",
        "fix": "APS-MES integration with real-time actual updates.",
    },
    {
        "mode": "Vendor abandonment",
        "description": "Implementer disappears after go-live. No optimization, no support.",
        "impact": "System degrades. Workarounds accumulate. Eventually shelfware.",
        "fix": "Managed services agreement. Post-go-live optimization cadence.",
    },
    {
        "mode": "Wrong tool for the job",
        "description": "APS selected based on vendor relationship, not plant requirements.",
        "impact": "Constant workarounds. The tool fights the process instead of enabling it.",
        "fix": "Vendor-agnostic selection based on actual constraints, data, and workflow.",
    },
]

# ---------------------------------------------------------------------------
# Operational vocabulary — how real people talk on the floor
# ---------------------------------------------------------------------------
FLOOR_LANGUAGE: Dict[str, List[str]] = {
    "scheduler_phrases": [
        "The schedule looked good until second shift",
        "I spend my morning replanning yesterday",
        "Nobody tells me about the machine being down until it's too late",
        "I've got three hot jobs and they all need the same machine",
        "Sales just promised a date without checking capacity",
        "The MRP dates are fiction — nobody even looks at them",
        "I'm the only one who knows the real sequence",
        "If I take a day off, everything falls apart",
        "We're always in expedite mode",
        "The plan is already wrong by Tuesday",
    ],
    "vp_ops_phrases": [
        "Why can't I get a straight answer on when this order will ship?",
        "Our on-time delivery is slipping and I don't know why",
        "We're running overtime every week but still missing dates",
        "I need visibility across all three plants, not three separate views",
        "The schedulers are doing their best, but they're flying blind",
        "Every time we add capacity, the bottleneck just moves",
        "We can't keep eating expedited freight costs",
        "Sales and operations are never on the same page",
        "How do we know if we can take this new order?",
        "We need to stop being reactive",
    ],
    "it_ot_phrases": [
        "Our ERP doesn't talk to the floor systems",
        "We have data everywhere but insight nowhere",
        "The integration broke and nobody noticed for two days",
        "We need real-time, not batch updates from last night",
        "How does this fit with our MES roadmap?",
        "We can't afford another point solution",
        "Who maintains this after go-live?",
        "ISA-95 is the framework, but our reality is messier",
    ],
    "supply_chain_phrases": [
        "We're carrying too much inventory but still stocking out",
        "Our forecast accuracy is terrible and the bullwhip effect is real",
        "S&OP is a monthly slide show, not a decision process",
        "We need ATP/CTP that actually reflects capacity",
        "Planning and execution live in different worlds",
        "We can't see across the supply chain — just our node",
    ],
}

# ---------------------------------------------------------------------------
# Digital transformation concepts
# ---------------------------------------------------------------------------
DIGITAL_TRANSFORMATION: Dict[str, str] = {
    "it_ot_convergence": (
        "The merging of Information Technology (business systems: ERP, APS, BI) with "
        "Operational Technology (floor systems: SCADA, PLC, MES, historians). "
        "Historically separate organizations, budgets, and architectures. Convergence "
        "is where scheduling intelligence meets real-time execution data. MDIF "
        "provides the architectural framework for this convergence."
    ),
    "digital_thread": (
        "An unbroken chain of data from design (CAD/PLM) through planning (ERP/APS) "
        "to execution (MES) and quality (QMS). In scheduling, the digital thread "
        "means a design change automatically updates routings, which updates the "
        "schedule, which updates the floor work instructions. Most manufacturers "
        "have breaks in this thread — usually at the planning-execution boundary."
    ),
    "digital_twin_scheduling": (
        "A virtual model of the production system that can simulate scheduling "
        "scenarios. Not just what-if on paper — a physics-based model that accounts "
        "for machine dynamics, material flow, and operator behavior. Used for "
        "capacity planning, line balancing, and disruption response. Emerging "
        "technology, but the foundation is good scheduling data."
    ),
    "ai_ml_in_planning": (
        "Machine learning for demand forecasting, predictive maintenance (feeding "
        "maintenance windows into the schedule), anomaly detection (catching "
        "schedule deviations early), and optimization (multi-objective scheduling "
        "across competing KPIs). AI doesn't replace the planner — it augments "
        "their decision-making with pattern recognition humans can't do at scale."
    ),
    "iiot_scheduling": (
        "IIoT sensors feeding real-time machine status, cycle times, and quality "
        "data into the scheduling system. Replaces manual data entry and yesterday's "
        "reports with live reality. When the schedule knows Machine 3 is running "
        "at 85% of standard rate right now, it adjusts downstream timing "
        "automatically."
    ),
}


# ---------------------------------------------------------------------------
# Assembly function — build the full domain context for prompts
# ---------------------------------------------------------------------------
def build_domain_context(
    industry: str | None = None,
    include_maturity: bool = False,
    include_objections: bool = True,
) -> str:
    """
    Build a domain knowledge context block for injection into LLM prompts.

    Args:
        industry: If provided, include industry-specific pain points.
        include_maturity: If True, include the scheduling maturity model.
        include_objections: If True, include objection handling knowledge.
    """
    sections = []

    # Core scheduling concepts (always included)
    concepts_text = "\n".join(
        [
            f"- {k.replace('_', ' ').title()}: {v}"
            for k, v in SCHEDULING_CONCEPTS.items()
        ]
    )
    sections.append(f"=== SCHEDULING EXPERTISE ===\n{concepts_text}")

    # Planning hierarchy (always included)
    hierarchy_text = "\n".join(
        [f"- {k.title()}: {v}" for k, v in PLANNING_HIERARCHY.items()]
    )
    sections.append(f"=== PLANNING HIERARCHY ===\n{hierarchy_text}")

    # Integration patterns (always included)
    integration_text = "\n".join(
        [
            f"- {k.replace('_', ' ').title()}: {v}"
            for k, v in INTEGRATION_PATTERNS.items()
        ]
    )
    sections.append(f"=== INTEGRATION KNOWLEDGE ===\n{integration_text}")

    # Key metrics (always included)
    metrics_text = "\n".join([f"- {k}: {v}" for k, v in METRICS.items()])
    sections.append(f"=== KEY METRICS ===\n{metrics_text}")

    # Industry-specific (optional)
    if industry and industry in INDUSTRY_PAIN_POINTS:
        ind = INDUSTRY_PAIN_POINTS[industry]
        pains = "\n".join([f"  - {p}" for p in ind["pain_points"]])
        sections.append(
            f"=== {ind['label'].upper()} — INDUSTRY SPECIFICS ===\n"
            f"Pain points:\n{pains}\n\n"
            f'What the scheduler says: "{ind["scheduler_says"]}"\n'
            f'What the VP says: "{ind["vp_says"]}"\n'
            f"Key metrics: {', '.join(ind['key_metrics'])}"
        )

    # Maturity model (optional)
    if include_maturity:
        levels = "\n\n".join(
            [
                f"Level {m['level']}:\n  {m['description']}\n"
                f"  Symptoms: {m['symptoms']}\n"
                f"  Move to next: {m['move_to_next']}"
                for m in MATURITY_MODEL
            ]
        )
        sections.append(f"=== SCHEDULING MATURITY MODEL ===\n{levels}")

    # Objections (optional)
    if include_objections:
        obj_text = "\n\n".join(
            [
                f'"{v["objection"]}"\n'
                f"  Quick answer: {v['surface_response']}\n"
                f"  Deep answer: {v['deep_response']}"
                for v in OBJECTION_RESPONSES.values()
            ]
        )
        sections.append(f"=== OBJECTION HANDLING ===\n{obj_text}")

    return "\n\n".join(sections)


def get_industry_context(industry_key: str) -> Dict[str, Any] | None:
    """Get industry-specific pain points and language for a given industry."""
    return INDUSTRY_PAIN_POINTS.get(industry_key)


def get_floor_language(persona: str = "scheduler_phrases") -> List[str]:
    """Get real operational language for a given persona."""
    return FLOOR_LANGUAGE.get(persona, [])
