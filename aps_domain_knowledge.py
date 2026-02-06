"""
APS (Advanced Planning and Scheduling) domain knowledge module.

Structured reference data for manufacturing scheduling concepts,
industry-specific pain points, integration patterns, metrics,
objection handling, maturity models, and operational language.

Used by the On Time Edge copy bot to ground generated content in
real manufacturing operations vocabulary and consulting expertise.
"""

from typing import Any, Dict, List, Optional


# ===========================================================================
# 1. PRODUCTION SCHEDULING CONCEPTS
# ===========================================================================

SCHEDULING_CONCEPTS: Dict[str, Any] = {
    "capacity_planning": {
        "finite_capacity": {
            "definition": (
                "Scheduling that respects actual resource limits — machines, labor, "
                "tools, materials — and will not overload a work center beyond what "
                "it can physically produce in a time period."
            ),
            "when_it_matters": (
                "Any environment where resources are genuinely constrained: "
                "bottleneck work centers, shared equipment, skilled-labor-limited "
                "operations. Most real shop floors."
            ),
            "erp_gap": (
                "Standard MRP/ERP treats capacity as infinite by default — it generates "
                "planned orders without checking whether the work center can actually "
                "handle the load. The result: overloaded schedules, expediting, and "
                "planners manually deconflicting in spreadsheets."
            ),
            "how_aps_handles_it": (
                "APS engines load operations against a capacity calendar, respecting "
                "shift patterns, maintenance windows, and concurrent resource limits. "
                "When a resource is full, the operation is moved forward or backward "
                "in time, or routed to an alternate resource."
            ),
        },
        "infinite_capacity": {
            "definition": (
                "Planning that assumes unlimited resource availability. Operations "
                "are scheduled based on due dates and lead times without checking "
                "whether the resource can handle the load."
            ),
            "where_its_used": (
                "Rough-cut capacity planning (RCCP), long-horizon demand planning, "
                "and legacy MRP runs. Useful for early-stage 'what does demand look "
                "like' analysis, but dangerous for detailed scheduling."
            ),
            "the_problem": (
                "Infinite capacity plans look perfect on paper. They fall apart the "
                "moment they hit the shop floor because they ignore the physical "
                "reality of resource constraints. This is why MRP-generated schedules "
                "are treated as suggestions, not commitments."
            ),
        },
    },
    "scheduling_direction": {
        "forward_scheduling": {
            "definition": (
                "Start from the earliest available time (now or material availability "
                "date) and schedule operations forward through the routing. The "
                "completion date is calculated, not fixed."
            ),
            "use_cases": [
                "Make-to-stock environments where you want to start ASAP",
                "Bottleneck loading — push work through the constraint as early as possible",
                "When you need to know 'when CAN we deliver' rather than 'when MUST we start'",
            ],
            "risk": (
                "Can build excessive WIP if not paired with release controls. "
                "Work arrives at downstream operations before they are ready."
            ),
        },
        "backward_scheduling": {
            "definition": (
                "Start from the due date and schedule operations backward to determine "
                "the latest start date. Minimizes WIP and aligns production with demand."
            ),
            "use_cases": [
                "Make-to-order and engineer-to-order environments",
                "JIT/lean operations where early completion creates inventory cost",
                "Customer-committed delivery dates that must be met",
            ],
            "risk": (
                "If the backward-scheduled start date is in the past, the order is "
                "already late before it begins. Requires a mechanism to flag 'past-due "
                "starts' and switch to forward scheduling for those orders."
            ),
        },
        "bidirectional_scheduling": {
            "definition": (
                "Schedule backward from the due date but forward from the bottleneck. "
                "The constraint is loaded first; upstream and downstream operations are "
                "scheduled relative to the constraint's timeline."
            ),
            "connection_to_toc": (
                "This is the scheduling logic behind Drum-Buffer-Rope. The bottleneck "
                "(drum) is scheduled first, buffers protect it, and the rope controls "
                "material release to prevent WIP buildup."
            ),
        },
    },
    "constraint_based_scheduling": {
        "definition": (
            "Scheduling that explicitly models and respects constraints beyond simple "
            "capacity: material availability, tooling, labor skills, regulatory holds, "
            "predecessor/successor dependencies, tank/vessel occupancy, curing times, "
            "and sequence-dependent setups."
        ),
        "constraint_types": {
            "primary_resources": "Machines, production lines, work centers",
            "secondary_resources": (
                "Tools, fixtures, molds, dies, jigs — often shared across machines "
                "and the real hidden bottleneck"
            ),
            "labor": (
                "Skilled operators, certified technicians, inspectors — especially "
                "constrained on second/third shifts and weekends"
            ),
            "materials": (
                "Raw material availability, subcomponent supply, shelf-life-limited "
                "ingredients, allocated vs. available inventory"
            ),
            "regulatory_holds": (
                "QA release holds, inspection gates, FDA batch record review, "
                "environmental permits (emissions windows)"
            ),
            "sequence_dependent_setups": (
                "Changeover times that vary based on what was run before and what "
                "runs next — color sequencing, allergen transitions, die changes, "
                "temperature transitions"
            ),
            "storage_and_staging": (
                "Tank occupancy, oven capacity, curing rack space, freezer/cooler "
                "capacity, staging area limits"
            ),
            "calendar_constraints": (
                "Shift patterns, planned maintenance windows, energy cost windows "
                "(off-peak scheduling), noise ordinances, CIP cleaning schedules"
            ),
        },
        "why_erp_cant_do_this": (
            "ERP scheduling modules model resources as simple capacity buckets. They "
            "cannot model the interactions between constraints — e.g., 'this machine "
            "needs this mold AND this operator AND the material must have completed "
            "a 4-hour drying cycle.' APS engines model these as simultaneous "
            "constraints with temporal relationships."
        ),
    },
    "theory_of_constraints": {
        "core_principle": (
            "A system's throughput is determined by its single tightest constraint "
            "(the bottleneck). Optimizing anything other than the constraint does not "
            "improve system throughput — it just builds WIP in front of the bottleneck "
            "or starves it."
        ),
        "five_focusing_steps": [
            "IDENTIFY the system's constraint (the resource with the least capacity relative to demand)",
            "EXPLOIT the constraint (maximize its utilization — no idle time, no quality waste on the bottleneck)",
            "SUBORDINATE everything else to the constraint (non-bottlenecks should feed the bottleneck, not run at full speed)",
            "ELEVATE the constraint (invest in more capacity only after exploitation and subordination)",
            "REPEAT — once a constraint is broken, a new one emerges; go back to step 1",
        ],
        "dbr": {
            "name": "Drum-Buffer-Rope",
            "drum": (
                "The bottleneck resource sets the pace (the 'drum beat') for the "
                "entire production system. The schedule is built around the constraint."
            ),
            "buffer": (
                "Time buffers placed before the constraint and before shipping to "
                "protect against variability. NOT safety stock — time buffers that "
                "ensure work arrives at the constraint early enough to keep it fed."
            ),
            "rope": (
                "A release mechanism that ties material release to the constraint's "
                "consumption rate. Prevents WIP explosion by controlling the rate at "
                "which new work enters the system."
            ),
            "simplified_dbr": (
                "S-DBR simplifies the model by using a single shipping buffer and "
                "a planned load calculation on the constraint. Easier to implement, "
                "works well for most job shops."
            ),
        },
        "ccpm": {
            "name": "Critical Chain Project Management",
            "definition": (
                "Applies TOC to project scheduling. Instead of adding safety time to "
                "each task (which gets wasted via Student Syndrome and Parkinson's Law), "
                "CCPM removes individual task safety margins and aggregates them into "
                "project and feeding buffers. Manages the critical chain (longest chain "
                "of dependent tasks considering resource contention) rather than the "
                "traditional critical path."
            ),
            "manufacturing_relevance": (
                "Applies to engineer-to-order, complex assembly, MRO, and capital "
                "project environments where the work is project-structured rather than "
                "repetitive flow."
            ),
            "buffer_management": (
                "Buffer consumption is tracked in real time: green (on track), yellow "
                "(watch), red (act now). This replaces traditional earned-value or "
                "milestone tracking with a forward-looking early-warning system."
            ),
        },
        "bottleneck_management": {
            "identifying_bottlenecks": [
                "Largest WIP queue — the bottleneck has the most work waiting in front of it",
                "Highest utilization — the resource consistently running at or near 100%",
                "Determines system throughput — if this resource stops, shipments stop",
                "Longest queue time — jobs wait longest before this operation",
                "Most frequent expediting target — when orders are late, this is where they get stuck",
            ],
            "common_mistakes": [
                "Treating every resource as a bottleneck (leads to overinvestment and no improvement)",
                "Optimizing non-bottlenecks (increases WIP without increasing throughput)",
                "Assuming the bottleneck is fixed (it shifts as product mix changes)",
                "Ignoring setup time on the bottleneck (every changeover minute is lost throughput)",
                "Running the bottleneck in large batches to reduce setups without considering downstream starvation",
            ],
            "wandering_bottleneck": (
                "In high-mix environments, the bottleneck shifts between resources as "
                "product mix changes. This makes static scheduling rules inadequate — "
                "you need dynamic, constraint-aware scheduling that re-identifies the "
                "active constraint continuously."
            ),
        },
    },
    "setup_optimization": {
        "smed": {
            "name": "Single-Minute Exchange of Die (SMED)",
            "definition": (
                "Shigeo Shingo's methodology for reducing changeover time by converting "
                "internal setup tasks (machine must be stopped) to external tasks "
                "(done while machine is running). Target: all changeovers under 10 minutes."
            ),
            "aps_interaction": (
                "APS uses changeover time data to evaluate sequence-dependent setup "
                "costs. The better the SMED data, the better the APS can optimize "
                "sequencing. Conversely, APS can quantify the throughput value of "
                "reducing specific changeover times, prioritizing SMED projects."
            ),
        },
        "sequence_dependent_setups": {
            "definition": (
                "Changeover time and cost that depend on both the outgoing and incoming "
                "product. A matrix of from-to times rather than a single fixed changeover."
            ),
            "examples": [
                "Color sequencing in plastics/paint: light-to-dark is fast, dark-to-light requires purging",
                "Allergen changeovers in food: peanut-to-non-peanut requires full teardown and sanitation",
                "Die changes in stamping: similar die sizes are quick, major size changes take hours",
                "Temperature transitions in heat treat: ramping up is faster than cooling down",
                "Product family grouping in pharma: same API to same API avoids full cleaning validation",
            ],
            "optimization_approaches": [
                "Campaign scheduling — group similar products to minimize changeovers",
                "Traveling salesman optimization — find the sequence that minimizes total setup time",
                "Setup matrix modeling — encode from/to changeover times for the APS to optimize against",
                "Family-based sequencing — define product families that share setup characteristics",
            ],
        },
    },
    "sequencing_rules": {
        "spt": {
            "name": "Shortest Processing Time",
            "rule": "Run the job with the shortest processing time next",
            "strength": "Minimizes average flow time and average WIP",
            "weakness": "Long jobs get perpetually delayed; bad for on-time delivery of large orders",
            "best_for": "High-volume environments where throughput matters more than individual due dates",
        },
        "edd": {
            "name": "Earliest Due Date",
            "rule": "Run the job with the earliest due date next",
            "strength": "Minimizes maximum lateness; intuitive for planners",
            "weakness": "Ignores processing time — a 5-minute job due tomorrow waits behind a 3-day job due today",
            "best_for": "Environments where on-time delivery is the primary KPI",
        },
        "cr": {
            "name": "Critical Ratio",
            "rule": "Priority = time remaining until due date / processing time remaining. Lower ratio = higher priority",
            "strength": "Dynamically balances urgency and workload; adapts as time passes",
            "weakness": "Can oscillate — priorities shift rapidly as due dates approach",
            "best_for": "Job shops with varying due dates and processing times",
        },
        "fifo": {
            "name": "First In, First Out",
            "rule": "Process jobs in the order they arrive at the queue",
            "strength": "Simple, fair, predictable; good for flow lines",
            "weakness": "Ignores due dates, priorities, and setup optimization; can create unnecessary changeovers",
            "best_for": "Stable flow environments with uniform products",
        },
        "wspt": {
            "name": "Weighted Shortest Processing Time",
            "rule": "Priority = weight (importance) / processing time. Higher ratio goes first",
            "strength": "Balances job importance with processing efficiency",
            "weakness": "Requires accurate weight assignments — politically charged in practice",
            "best_for": "Environments with tiered customer priorities (e.g., A/B/C customers)",
        },
        "ato": {
            "name": "ATO / Slack-Based Rules",
            "rule": "Priority based on remaining slack = (due date - now - remaining processing time). Less slack = higher priority",
            "strength": "Focuses on jobs most at risk of being late",
            "weakness": "Requires accurate remaining processing time estimates",
            "best_for": "Complex job shops with long routings and multiple operations",
        },
        "bottleneck_first": {
            "name": "Bottleneck-First Sequencing",
            "rule": (
                "Schedule the bottleneck resource first using the best rule for system "
                "throughput, then schedule non-bottleneck resources to support the "
                "bottleneck schedule"
            ),
            "strength": "Maximizes system throughput; aligned with TOC",
            "weakness": "Requires accurate identification of the bottleneck, which can shift",
            "best_for": "Any environment with a clearly identified constraint",
        },
        "practical_reality": (
            "No single dispatching rule works universally. Real APS systems use "
            "multi-criteria optimization: weighted combinations of due date, priority, "
            "setup cost, material availability, and downstream impact. The rules above "
            "are building blocks, not solutions."
        ),
    },
    "batch_and_lot_sizing": {
        "fixed_batch": {
            "definition": "Production quantity is a fixed multiple (e.g., always produce in lots of 500)",
            "pros": "Simple, predictable, easy to plan",
            "cons": "Creates excess inventory when demand doesn't match batch size",
        },
        "lot_for_lot": {
            "definition": "Produce exactly what is needed for each demand period",
            "pros": "Minimizes inventory; ideal for expensive or perishable items",
            "cons": "Maximizes setups; only practical when changeover cost is low",
        },
        "eoq": {
            "name": "Economic Order Quantity / Economic Batch Quantity",
            "definition": "Batch size that minimizes the total of setup cost and holding cost",
            "pros": "Mathematically optimal for steady-state demand",
            "cons": (
                "Assumes stable demand and known costs — rarely true in practice. "
                "Also ignores capacity constraints entirely."
            ),
        },
        "period_order_quantity": {
            "definition": "Cover a fixed number of demand periods per batch (e.g., 2 weeks of demand)",
            "pros": "Adapts batch size to actual demand; reduces nervous replanning",
            "cons": "Doesn't consider setup cost trade-offs",
        },
        "campaign_scheduling": {
            "definition": (
                "Group production of the same or similar products into campaigns (runs), "
                "minimizing changeovers while building inventory to cover demand during "
                "campaigns of other products."
            ),
            "use_cases": [
                "Pharma — campaign by API to avoid full cleaning validation between batches",
                "Food — campaign by allergen class to minimize sanitation changeovers",
                "Plastics — campaign by color family (light to dark sequence within a campaign)",
                "Metals — campaign by alloy/grade to minimize furnace transition times",
                "CPG — campaign by packaging format before switching line configurations",
            ],
            "key_trade_off": (
                "Longer campaigns = fewer changeovers but higher inventory and longer "
                "lead times for other products. The optimal campaign length balances "
                "setup cost/time against inventory carrying cost and service level risk."
            ),
        },
        "transfer_batch_vs_process_batch": {
            "definition": (
                "Process batch: how many units you make before changing over. "
                "Transfer batch: how many units you move to the next operation at once. "
                "These do not need to be the same."
            ),
            "toc_insight": (
                "Splitting the transfer batch (moving partial batches downstream before "
                "the full process batch is complete) reduces lead time dramatically. "
                "A batch of 1000 with a transfer batch of 100 means downstream starts "
                "after 100 units, not 1000. This is one of the most powerful and "
                "underused scheduling levers."
            ),
        },
    },
}


# ===========================================================================
# 2. INDUSTRY-SPECIFIC SCHEDULING PAIN POINTS
# ===========================================================================

INDUSTRY_PAIN_POINTS: Dict[str, Dict[str, Any]] = {
    "aerospace": {
        "display_name": "Aerospace and Defense",
        "characteristics": [
            "Long lead times (months to years for complex assemblies)",
            "Deep, multi-level BOMs (thousands of components per assembly)",
            "Low volume, high mix, high complexity",
            "Strict regulatory requirements (AS9100, ITAR, NADCAP)",
            "Government contract compliance (DFARS, DCMA oversight)",
            "Project-based production (not repetitive flow)",
        ],
        "scheduling_pain_points": {
            "bom_complexity": (
                "Bills of material with 10-20+ levels, thousands of parts, and "
                "long-lead procurement items that must be synchronized. A single "
                "missing fastener can hold up a multi-million-dollar assembly."
            ),
            "long_lead_procurement": (
                "Castings, forgings, and specialty alloys with 6-18 month lead times. "
                "Scheduling must account for supplier lead time variability and "
                "coordinate material arrival with capacity availability."
            ),
            "regulatory_holds": (
                "AS9100 and NADCAP require inspection holds, first-article inspections, "
                "and process qualification steps that create scheduling gates. These "
                "are not optional and cannot be expedited."
            ),
            "mro_scheduling": (
                "Maintenance, Repair, and Overhaul work is inherently uncertain — you "
                "don't know the full scope of work until teardown and inspection. "
                "Scheduling must handle progressive discovery: plan based on expected "
                "scope, then replan as actual condition is revealed."
            ),
            "engineering_changes": (
                "Frequent ECOs (Engineering Change Orders) that alter routings, BOMs, "
                "and specifications mid-production. The schedule must absorb these "
                "changes without cascading delays."
            ),
            "skilled_labor": (
                "Certified welders, NDT inspectors, and specialty machinists are scarce. "
                "The constraint is often labor certification, not machine availability."
            ),
        },
        "what_schedulers_say": [
            "I can't even see all the parts I need to track across 5 levels of the BOM",
            "We have 200 open jobs and I need to know which ones are actually going to be late",
            "The schedule looks great until purchasing tells me the forgings slipped 8 weeks",
            "MRO is a nightmare — every induction is a snowflake",
            "We spend more time expediting than scheduling",
        ],
        "kpis_that_matter": [
            "On-time delivery to customer commit dates",
            "Flow days (total days from release to completion)",
            "WIP value ($M tied up on the floor)",
            "Past-due backlog value",
            "First-pass yield at inspection gates",
            "Schedule adherence (did we execute what we planned?)",
        ],
    },
    "automotive": {
        "display_name": "Automotive",
        "characteristics": [
            "High volume, repetitive flow with mixed-model assembly",
            "JIT/JIS delivery requirements from OEMs",
            "Takt time-driven production lines",
            "Tiered supplier hierarchy (Tier 1/2/3)",
            "Strict packaging and labeling standards (AIAG)",
            "Seasonal model changeovers and new program launches",
        ],
        "scheduling_pain_points": {
            "jit_jis": (
                "Just-In-Time and Just-In-Sequence delivery to OEM assembly lines. "
                "Parts must arrive at the exact dock, at the exact time, in the exact "
                "sequence the OEM will install them. A 15-minute delay can shut down "
                "an OEM line at $10,000-50,000 per minute in penalty costs."
            ),
            "takt_time": (
                "Every station on the line must complete its work within the takt time "
                "(available production time / customer demand rate). If any station "
                "exceeds takt, the entire line slows. Scheduling must balance line "
                "loading across stations and manage model mix to avoid takt violations."
            ),
            "mixed_model_lines": (
                "Producing multiple vehicle variants on the same line. The sequence must "
                "balance labor content (avoid clustering high-content models), material "
                "presentation (different parts per variant), and option-specific tooling."
            ),
            "supplier_synchronization": (
                "Tier 1 suppliers must synchronize their production with OEM broadcast "
                "schedules (830/862 EDI transactions). Schedule changes propagate upstream "
                "through the supply chain, amplifying variability (bullwhip effect)."
            ),
            "launch_management": (
                "New model launches require parallel scheduling of current production "
                "wind-down, tooling changeover, trial builds, and ramp-up. The transition "
                "window is measured in days, not weeks."
            ),
            "premium_freight": (
                "When scheduling fails, the cost manifests as premium freight — expedited "
                "shipping to avoid line-down situations. A single premium freight event "
                "can cost $20,000-100,000. Reducing premium freight is often the ROI "
                "case for APS in automotive."
            ),
        },
        "what_schedulers_say": [
            "If we miss one sequence delivery, we're paying for the OEM's downtime",
            "I get 3 schedule changes per day from the customer and each one cascades",
            "We need to know RIGHT NOW if we can hit tomorrow's shipments",
            "The line is balanced for the average mix but today's mix is 60% high-content",
            "Premium freight is eating our margin — we shipped $400K in air freight last quarter",
        ],
        "kpis_that_matter": [
            "OTD to OEM (measured in minutes, not days)",
            "Premium freight cost ($)",
            "Takt time adherence",
            "Line uptime / OEE",
            "PPM (parts per million defective — quality)",
            "Sequence accuracy (JIS compliance %)",
        ],
    },
    "food_and_beverage": {
        "display_name": "Food and Beverage",
        "characteristics": [
            "Perishable raw materials and finished goods (shelf life constraints)",
            "Allergen management (regulatory and liability driven)",
            "Seasonal and promotional demand spikes",
            "Process manufacturing (batch/continuous, not discrete)",
            "CIP (Clean-In-Place) cleaning requirements between products",
            "Yield variability based on raw material quality",
            "FSMA (Food Safety Modernization Act) compliance",
        ],
        "scheduling_pain_points": {
            "shelf_life": (
                "Raw materials expire. WIP expires. Finished goods expire. The schedule "
                "must consider remaining shelf life at every stage — you can't schedule "
                "a batch of yogurt starter that will expire before the filling line is "
                "available. FEFO (First Expired, First Out) sequencing adds complexity."
            ),
            "allergen_changeovers": (
                "Producing a peanut product before a peanut-free product requires a "
                "full teardown, cleaning, and allergen validation. This can take 4-8 "
                "hours. The schedule must sequence products to minimize allergen "
                "transitions or batch allergen-containing products together."
            ),
            "cip_cleaning": (
                "Clean-In-Place cycles between production runs consume 1-4 hours of "
                "equipment time. CIP frequency depends on product type, time elapsed, "
                "and regulatory requirements. The schedule must account for CIP as a "
                "non-negotiable constraint, not optional downtime."
            ),
            "seasonal_demand": (
                "Demand for many food products is highly seasonal (beverages in summer, "
                "baking ingredients in Q4, snacks around sporting events). Production "
                "must build ahead, requiring coordination between campaign scheduling "
                "and warehouse capacity."
            ),
            "yield_variability": (
                "Agricultural raw materials vary in quality, moisture content, and yield. "
                "A batch of tomatoes might yield 10% more or less sauce than planned. "
                "The schedule must handle this variability without creating shortages "
                "or overproduction."
            ),
            "co_manufacturing": (
                "Contract manufacturing / co-packing for multiple brands on shared lines. "
                "Each brand has its own specs, packaging, and quality requirements. "
                "Scheduling must manage brand changeovers and segregation requirements."
            ),
        },
        "what_schedulers_say": [
            "I have 4 hours of CIP between allergen groups — that's half a shift gone",
            "The strawberries arrived but they're not ripe enough — reschedule the jam line",
            "We need to run the BBQ sauce campaign next week but the tanks are allocated to ketchup",
            "Walmart just doubled their promotional order and the promo starts in 10 days",
            "If we don't ship this by Thursday, it won't have enough shelf life for the retailer to accept it",
            "We're throwing away $50K of ingredients a month because batches expire waiting for packaging",
        ],
        "kpis_that_matter": [
            "OTD to retailer/distributor DC",
            "Waste/scrap rate (expired ingredients and finished goods)",
            "Changeover time (especially allergen transitions)",
            "OEE on filling/packaging lines",
            "Inventory turns (critical with perishable goods)",
            "Case fill rate (% of ordered cases shipped complete)",
            "FSMA compliance score",
        ],
    },
    "pharma_life_sciences": {
        "display_name": "Pharmaceutical and Life Sciences",
        "characteristics": [
            "GMP (Good Manufacturing Practice) compliance — FDA 21 CFR Parts 210/211",
            "Batch record documentation (every action, every deviation, every signature)",
            "Equipment qualification and validation (IQ/OQ/PQ)",
            "Campaign scheduling driven by cleaning validation requirements",
            "Long lead times for API (Active Pharmaceutical Ingredient) procurement",
            "Multi-site, multi-country regulatory requirements",
            "Serialization and track-and-trace requirements",
        ],
        "scheduling_pain_points": {
            "gmp_compliance": (
                "Every scheduling decision must be defensible in an FDA audit. You can't "
                "move a batch to an unvalidated vessel. You can't skip a hold time. You "
                "can't use an out-of-calibration instrument. The schedule must enforce "
                "regulatory constraints, not just suggest them."
            ),
            "batch_records": (
                "Batch records (now often electronic — eBR) must be completed, reviewed, "
                "and approved before product can be released. This creates a scheduling "
                "dependency: the QA review queue becomes a hidden bottleneck that APS "
                "must account for."
            ),
            "campaign_scheduling": (
                "Pharmaceutical campaigns group batches of the same product to avoid "
                "full cleaning validation between batches. Switching from Product A to "
                "Product B may require a 24-72 hour validated cleaning procedure with "
                "swab testing and QA release. Campaign length balances cleaning cost "
                "against inventory carrying cost and demand coverage."
            ),
            "equipment_qualification": (
                "Each vessel, reactor, lyophilizer, and filling line must be qualified "
                "for each product. If equipment fails or requires requalification, the "
                "schedule must find an alternate qualified resource — and there may not "
                "be one."
            ),
            "stability_and_hold_times": (
                "Intermediate products have maximum hold times (e.g., a bulk solution "
                "must be filled within 48 hours of compounding). The schedule must "
                "ensure downstream operations start within the hold time window — "
                "a constraint that tightly couples sequential operations."
            ),
            "regulatory_filings": (
                "Manufacturing processes are defined in regulatory filings (ANDA, NDA, "
                "MAA). Any process change requires a regulatory supplement. This means "
                "you can't simply change routings or add alternate resources without "
                "regulatory impact assessment. The schedule is constrained by what's "
                "in the filing."
            ),
        },
        "what_schedulers_say": [
            "We have 48 hours to fill this bulk or it goes to waste — that's $200K",
            "QA is reviewing 15 batch records and we can't ship until they're released",
            "We need a 3-day cleaning validation to switch from Product A to Product B",
            "The lyophilizer is our bottleneck and it's booked for 6 weeks",
            "We can't move this batch to Reactor 3 — it's not qualified for this product",
            "The FDA is coming in 3 months and every deviation on the schedule is a finding",
        ],
        "kpis_that_matter": [
            "Batch cycle time (from weigh-and-dispense to QA release)",
            "Right-first-time rate (batches completed without deviation)",
            "Campaign length optimization (batches per campaign)",
            "Equipment utilization (especially constrained assets like lyophilizers)",
            "Cleaning validation turnaround time",
            "QA release queue time (hidden lead time)",
            "OTD to distribution (especially for market-launch products)",
        ],
    },
    "medical_device": {
        "display_name": "Medical Device",
        "characteristics": [
            "FDA 21 CFR Part 820 (Quality System Regulation)",
            "ISO 13485 quality management system",
            "Full device history record (DHR) traceability",
            "UDI (Unique Device Identification) requirements",
            "Sterilization scheduling (EtO, gamma, e-beam)",
            "Cleanroom production constraints",
            "Design controls and design transfer requirements",
        ],
        "scheduling_pain_points": {
            "traceability": (
                "Every component, every lot, every operator, every machine, every "
                "environmental condition must be traceable for every device produced. "
                "The schedule must ensure traceability data is captured at each step "
                "— this means MES integration is not optional."
            ),
            "sterilization_scheduling": (
                "EtO (ethylene oxide) sterilization cycles take 12-72 hours including "
                "aeration. Gamma and e-beam may require off-site processing with "
                "transport logistics. Sterilization is often the final bottleneck "
                "before shipment, and load optimization (filling sterilization chambers "
                "efficiently) is a scheduling problem in itself."
            ),
            "cleanroom_constraints": (
                "Production in ISO Class 5-8 cleanrooms limits the number of people, "
                "equipment, and WIP that can be in the room simultaneously. Gowning "
                "requirements and airlock transitions add to changeover time. The "
                "cleanroom itself is a constrained resource."
            ),
            "validation_requirements": (
                "Process validation (IQ/OQ/PQ) must be completed and documented before "
                "production on any new or modified equipment. Validation runs consume "
                "production capacity and must be scheduled alongside commercial production."
            ),
            "complaint_driven_urgency": (
                "Field complaints and CAPA (Corrective and Preventive Action) activities "
                "can require immediate production of replacement lots, disrupting the "
                "existing schedule. These must be prioritized while maintaining "
                "traceability and quality records."
            ),
        },
        "what_schedulers_say": [
            "The sterilizer is full but I have 3 more lots that need to ship Friday",
            "Cleanroom 2 is down for requalification — where do I put these assemblies?",
            "I need to track lot numbers for every component in this assembly and my system can't do it",
            "We have a CAPA lot that jumped the queue and now everything else is late",
            "The DHR review is taking 3 days per lot — that's our real bottleneck",
        ],
        "kpis_that_matter": [
            "OTD (especially for hospital orders and distributor backorders)",
            "DHR completion time (from production to record closure)",
            "Sterilization capacity utilization",
            "Cleanroom utilization and throughput",
            "CAPA lot turnaround time",
            "First-pass yield (critical for validated processes)",
            "Inventory accuracy (lot-level, not just SKU-level)",
        ],
    },
    "metals": {
        "display_name": "Metals and Metal Parts",
        "characteristics": [
            "Heat/melt scheduling with furnace constraints",
            "Alloy and grade management (material segregation)",
            "Trim/cut optimization (yield maximization)",
            "Hot and cold processing sequences with temperature constraints",
            "Energy-intensive operations (cost-sensitive to utility rates)",
            "Long processing times (heat treat cycles of 8-72 hours)",
        ],
        "scheduling_pain_points": {
            "heat_melt_scheduling": (
                "Furnace/melt scheduling is the defining constraint in metals. Each heat "
                "has a minimum and maximum charge weight, specific alloy composition, "
                "and temperature/time profile. Heats must be grouped by alloy to avoid "
                "cross-contamination. The melt schedule drives the entire downstream "
                "production plan."
            ),
            "coil_slab_optimization": (
                "In flat-rolled products, coil or slab optimization involves cutting "
                "master coils/slabs to minimize trim waste while satisfying multiple "
                "customer orders of different widths and gauges. This is a 2D cutting "
                "stock problem that interacts with scheduling."
            ),
            "furnace_sequencing": (
                "Heat treat furnaces have long cycle times (8-72 hours) and batch "
                "constraints (must fill to minimum, cannot exceed maximum load). "
                "Sequencing must group compatible parts/alloys and optimize furnace "
                "loading. Temperature transitions between different heat treat profiles "
                "add significant changeover time."
            ),
            "energy_cost": (
                "Electric arc furnaces, induction furnaces, and heat treat ovens consume "
                "massive energy. Scheduling to off-peak utility rates can save "
                "$100K-$1M annually. The schedule must consider time-of-use energy "
                "pricing as a constraint."
            ),
            "alloy_segregation": (
                "Different alloys and grades must be physically segregated throughout "
                "processing. A mix-up can contaminate an entire heat or batch. "
                "Scheduling must ensure alloy-compatible grouping at every stage."
            ),
        },
        "what_schedulers_say": [
            "I need to fill this heat to 40 tons but I only have 32 tons of orders for this alloy",
            "The furnace takes 16 hours per cycle — I can only run 3 heats per day and I need 5",
            "We're paying peak-rate electricity to run the EAF because the schedule slipped",
            "I have 20 customer orders that need to come out of this master coil — which ones do I cut first?",
            "The heat treat oven is my bottleneck but half the time it's running at 60% load",
        ],
        "kpis_that_matter": [
            "Yield (lbs shipped / lbs melted — every % point matters)",
            "Furnace utilization (charged weight / max capacity)",
            "Energy cost per ton produced",
            "OTD to customer promise date",
            "Trim waste percentage",
            "Heat-to-ship cycle time",
            "Alloy changeover frequency",
        ],
    },
    "cpg": {
        "display_name": "Consumer Packaged Goods",
        "characteristics": [
            "High volume, high mix — hundreds to thousands of SKUs",
            "Promotional demand spikes (retailer promotions, seasonal)",
            "Co-packing and private label production",
            "Short product lifecycles and frequent SKU launches/discontinuations",
            "Retailer compliance requirements (OTIF penalties — Walmart, Target, etc.)",
            "High changeover frequency on packaging lines",
        ],
        "scheduling_pain_points": {
            "sku_proliferation": (
                "CPG companies often manage 500-5000+ SKUs across multiple production "
                "lines. Each SKU may have unique packaging, labeling, and sizing. The "
                "scheduling challenge is managing changeover frequency while maintaining "
                "service levels across the full portfolio."
            ),
            "promotional_demand": (
                "Retailer promotions can spike demand 3-10x for specific SKUs with 2-4 "
                "weeks notice. Building promotional inventory requires campaign "
                "scheduling on top of the base production plan, often displacing other "
                "SKUs and creating cascading scheduling conflicts."
            ),
            "otif_penalties": (
                "Major retailers (Walmart's OTIF program, Target, Kroger) impose "
                "financial penalties for late or incomplete shipments — typically 3% "
                "of invoice value. A 95% OTIF target sounds high but means 1 in 20 "
                "shipments can fail. At scale, this costs millions. The schedule must "
                "directly optimize for OTIF, not just production efficiency."
            ),
            "co_packing": (
                "Contract manufacturing for multiple brands on shared lines. Each brand "
                "has unique specifications, packaging, and quality requirements. "
                "Scheduling must manage brand segregation, changeovers, and allocation "
                "of shared capacity across customers."
            ),
            "line_speed_variability": (
                "Packaging line speeds vary by SKU: different container sizes, label "
                "types, closure mechanisms, and case configurations. The schedule must "
                "use SKU-specific run rates, not averages, to accurately predict "
                "completion times."
            ),
        },
        "what_schedulers_say": [
            "I have 200 SKUs and 4 lines — I'm changing over 8 times a shift",
            "Walmart just told us there's a promo in 3 weeks and I need 3x volume of that SKU",
            "We're at 92% OTIF and every miss is costing us $15K in penalties",
            "The co-pack run for Brand X pushed everything else back and now we're short on our own brand",
            "I need to know if I can say yes to this new private-label contract without killing my service levels",
        ],
        "kpis_that_matter": [
            "OTIF % to retailers (the metric that drives revenue protection)",
            "Changeover time and frequency",
            "Case fill rate",
            "Inventory days of supply (by SKU)",
            "Line OEE (availability x performance x quality)",
            "Promotional forecast accuracy",
            "SKU rationalization impact on schedule complexity",
        ],
    },
    "plastics": {
        "display_name": "Plastics and Rubber",
        "characteristics": [
            "Mold/tool-constrained production (molds are expensive, shared assets)",
            "Color sequencing requirements (purge time between colors)",
            "Material drying and preparation requirements",
            "Multi-cavity molds with varying cycle times",
            "Insert molding and overmolding with upstream dependencies",
            "High setup time for mold changes (30 min to 4+ hours)",
        ],
        "scheduling_pain_points": {
            "mold_changeovers": (
                "Mold changes on injection molding machines are the dominant scheduling "
                "constraint. A change can take 30 minutes to 4+ hours depending on mold "
                "size, machine tonnage, and cooling/heating requirements. The mold is "
                "often a secondary resource shared across multiple machines, creating "
                "a combinatorial scheduling challenge."
            ),
            "color_sequencing": (
                "Running dark colors after light colors is fast (minimal purging). "
                "Running light after dark requires extensive purging (30-90 minutes "
                "and significant material waste). Optimal scheduling sequences colors "
                "from light to dark within a campaign, then does a full purge before "
                "restarting."
            ),
            "material_drying": (
                "Many resins (nylon, PET, PC, ABS) require 2-8 hours of drying before "
                "processing. If the dryer isn't started in time, the machine sits idle. "
                "Material drying is an upstream constraint that must be pre-scheduled "
                "to align with machine availability."
            ),
            "mold_availability": (
                "Expensive molds ($50K-$500K+) are shared across machines. A mold can "
                "only be in one machine at a time. When demand for products sharing a "
                "mold exceeds single-machine capacity, the schedule must manage mold "
                "transfers — which means coordinating teardown on one machine with "
                "setup on another."
            ),
            "cycle_time_sensitivity": (
                "Injection molding cycle times are measured in seconds (15-120s typical). "
                "A 2-second cycle time increase across a 24-hour run of a 4-cavity mold "
                "costs hundreds of parts. The schedule must use actual cycle times per "
                "part/mold/machine combination, not averages."
            ),
        },
        "what_schedulers_say": [
            "I have 30 molds and 12 machines — I spend my whole day figuring out which mold goes where",
            "We ran black after white and lost 45 minutes purging — that's 2000 parts we didn't make",
            "The dryer wasn't started and now the machine is sitting idle for 4 hours",
            "Customer X needs their part but the mold is in Machine 7 running Customer Y's order",
            "The schedule says 10,000 parts but the cycle time on this machine is 2 seconds slower",
        ],
        "kpis_that_matter": [
            "Machine utilization (uptime vs. changeover vs. idle vs. unplanned downtime)",
            "Mold changeover time and frequency",
            "Scrap rate (startup scrap, color change scrap, quality rejects)",
            "Cycle time vs. standard (actual vs. expected)",
            "Material waste from purging",
            "OTD to customer",
            "OEE by machine",
        ],
    },
}


# ===========================================================================
# 3. INTEGRATION PATTERNS
# ===========================================================================

INTEGRATION_PATTERNS: Dict[str, Any] = {
    "isa_95_levels": {
        "overview": (
            "ISA-95 (IEC 62264) defines a hierarchical model for manufacturing "
            "systems integration. APS operates at Level 3 (Manufacturing Operations "
            "Management) and bridges between Level 4 (Business Planning & Logistics / "
            "ERP) and Levels 0-2 (Shop Floor Control / SCADA / PLC)."
        ),
        "levels": {
            "level_4": {
                "name": "Business Planning and Logistics",
                "systems": "ERP, demand planning, supply chain planning, financial systems",
                "aps_interaction": (
                    "APS receives demand (sales orders, forecasts, planned orders) and "
                    "master data (BOMs, routings, resource calendars) from ERP. APS sends "
                    "back production schedules, planned start/end times, and capacity "
                    "plans. This is the most common integration point."
                ),
                "data_flow_down": [
                    "Sales orders and forecasts (what to make and when)",
                    "BOMs and routings (how to make it)",
                    "Inventory levels (what's on hand and allocated)",
                    "Purchase order status (when materials arrive)",
                    "Resource calendars (shifts, maintenance, holidays)",
                    "Work order status updates",
                ],
                "data_flow_up": [
                    "Finite-capacity production schedule (planned start/end per operation)",
                    "Capacity utilization reports",
                    "Projected completion dates (ATP / CTP)",
                    "Rescheduling recommendations",
                    "Material requirements timing (when to release POs)",
                ],
            },
            "level_3": {
                "name": "Manufacturing Operations Management",
                "systems": "MES, APS, QMS, LIMS, WMS, maintenance management",
                "aps_interaction": (
                    "APS provides the detailed schedule to MES for execution. MES "
                    "provides actual production data back to APS for rescheduling: "
                    "actual start/end times, quantities produced, quality results, "
                    "and equipment status."
                ),
                "data_flow_to_mes": [
                    "Detailed operation schedule (what to run, when, on which resource)",
                    "Sequence instructions (run order within a work center)",
                    "Setup instructions (what's changing and changeover procedure)",
                    "Material staging requirements (what to stage and when)",
                ],
                "data_flow_from_mes": [
                    "Actual production events (operation start, end, interruption)",
                    "Quantities produced (good, scrap, rework)",
                    "Actual resource utilization and downtime events",
                    "Quality inspection results (pass/fail/hold)",
                    "Labor time and attendance by operation",
                ],
            },
            "level_2": {
                "name": "Supervisory Control",
                "systems": "SCADA, HMI, DCS",
                "aps_interaction": (
                    "APS typically does not integrate directly with Level 2. MES or "
                    "an OEE system bridges this gap, translating SCADA/PLC events into "
                    "production status that APS can consume."
                ),
            },
            "level_1_0": {
                "name": "Direct Control / Process",
                "systems": "PLCs, sensors, actuators, instruments",
                "aps_interaction": (
                    "No direct integration. Data flows through SCADA/MES/historians "
                    "and is consumed by APS as aggregated production events."
                ),
            },
        },
    },
    "isa_88": {
        "overview": (
            "ISA-88 (IEC 61512) defines standards for batch control in process "
            "industries. It separates the recipe (what to make) from the equipment "
            "(what to make it on) through a modular model: procedure, unit procedure, "
            "operation, phase."
        ),
        "aps_relevance": (
            "In process manufacturing (pharma, food, chemicals), APS must understand "
            "ISA-88 concepts: master recipes vs. control recipes, equipment modules, "
            "and batch execution models. The APS schedules at the 'unit procedure' "
            "level — assigning recipe steps to equipment units with time constraints."
        ),
    },
    "erp_integration": {
        "sap": {
            "common_integration_points": [
                "PP (Production Planning) — planned orders, production orders, BOMs, routings",
                "MM (Materials Management) — inventory, purchase orders, goods receipts",
                "SD (Sales & Distribution) — sales orders, deliveries, ATP",
                "PM (Plant Maintenance) — maintenance orders, equipment availability",
                "QM (Quality Management) — inspection lots, quality notifications",
            ],
            "integration_methods": [
                "RFC/BAPI — real-time function calls for transactional data",
                "IDoc — asynchronous document exchange for batch data transfers",
                "SAP PI/PO (Process Integration) — middleware-based integration",
                "SAP Integration Suite / BTP — cloud-native integration platform",
                "Direct database read (not recommended — bypasses SAP business logic)",
                "OData / REST APIs — modern integration for S/4HANA",
            ],
            "common_failures": [
                "Routing data in SAP doesn't match actual shop floor operations (operations added/removed without updating SAP)",
                "BOM levels too deep or too shallow for APS granularity",
                "Work center capacity in SAP doesn't reflect actual shift patterns and maintenance windows",
                "Master data quality issues — missing or incorrect setup times, run times, and scrap factors",
                "Batch job timing conflicts — APS and SAP scheduled to sync at the same time, causing data locks",
            ],
        },
        "oracle": {
            "common_integration_points": [
                "Oracle Manufacturing (WIP, BOM, Routing) — work orders, resource data",
                "Oracle Inventory — on-hand, reservations, lot/serial tracking",
                "Oracle Order Management — sales orders, schedules",
                "Oracle Purchasing — PO status, receipt dates",
                "Oracle Quality — inspection plans, results",
            ],
            "integration_methods": [
                "Oracle Integration Cloud (OIC) — cloud-native middleware",
                "SOA Gateway / REST APIs — for Oracle Cloud applications",
                "Open Interface tables — batch import/export via staging tables",
                "Database links — direct table access (legacy, not recommended for cloud)",
                "FBDI (File-Based Data Import) — for Oracle Fusion/Cloud",
            ],
            "common_failures": [
                "Oracle's native scheduling (often ASCP) conflicts with APS — dual scheduling creates confusion",
                "Routing flexibility in Oracle is limited — alternate routings are cumbersome",
                "Oracle Cloud vs. On-Prem integration patterns are fundamentally different — migration breaks integrations",
            ],
        },
        "dynamics_365": {
            "common_integration_points": [
                "D365 Supply Chain Management — production orders, master planning (MRP/Planning Optimization)",
                "D365 Finance — cost data, financial calendars",
                "Dataverse — common data platform for Power Platform integration",
            ],
            "integration_methods": [
                "OData REST APIs — primary modern integration method",
                "Data Management Framework (DMF/DIXF) — batch import/export",
                "Dual-write — real-time sync between D365 and Dataverse",
                "Azure Service Bus / Logic Apps — event-driven integration",
                "Power Automate — low-code integration for simpler flows",
            ],
            "common_failures": [
                "Planning Optimization in D365 conflicts with external APS — must disable native planning to avoid dual scheduling",
                "Data entity performance issues at high volume — OData calls time out with large datasets",
                "Customizations (X++ extensions) break during D365 updates — integration must be resilient to schema changes",
            ],
        },
    },
    "mes_integration": {
        "purpose": (
            "MES is the execution engine; APS is the planning engine. The integration "
            "between them is the most critical for schedule accuracy because MES provides "
            "real-time feedback on what's actually happening on the floor."
        ),
        "critical_data_flows": {
            "aps_to_mes": [
                "Dispatched work order sequence (priority-ordered list of what to run next)",
                "Expected start/end times per operation",
                "Resource assignments (which machine, which operator)",
                "Setup instructions and sequence",
                "Material staging requirements",
            ],
            "mes_to_aps": [
                "Actual operation start/end (for rescheduling remaining work)",
                "Actual quantities produced (good, scrap, rework)",
                "Equipment status changes (running, down, setup, idle)",
                "Quality hold events (stop downstream operations until released)",
                "Labor actuals (who worked on what, for how long)",
            ],
        },
        "common_platforms": [
            "Sepasoft (MES modules on Ignition — strong SCADA integration)",
            "Parsec TrakSYS (OEE + MES + SPC in one platform)",
            "AVEVA MES (formerly Wonderware — strong in process industries)",
            "GE Vernova / Proficy (MES/MOM/historian — strong in discrete)",
            "Rockwell Plex / FactoryTalk ProductionCentre",
            "SAP ME/MII (SAP's native MES — tight SAP integration)",
            "Fuuz by MFGx (AI-enabled MES/WMS/QMS)",
            "42Q (cloud MES — strong in electronics/medical device)",
            "Aegis FactoryLogix (electronics/PCB assembly focused)",
        ],
        "integration_challenges": [
            "Schedule horizon mismatch — APS plans in days/weeks, MES executes in minutes/hours",
            "Event granularity — MES captures machine-level events; APS needs operation-level summaries",
            "Rescheduling frequency — how often should APS update the MES dispatch list? Too often creates instability, too rarely creates drift",
            "Who owns the truth — when MES actual and APS planned diverge, which system drives the decision?",
            "Exception handling — when a machine goes down, does MES reroute locally or does APS reschedule globally?",
        ],
    },
    "oee_integration": {
        "purpose": (
            "OEE systems capture real-time equipment performance data. APS uses this "
            "data to improve schedule accuracy: actual run rates (vs. standard), "
            "actual downtime patterns, and quality yields."
        ),
        "data_aps_consumes": [
            "Actual cycle times by product/machine combination (not standards — actuals)",
            "Downtime events by category (planned maintenance, breakdown, changeover, material wait, etc.)",
            "Quality yield by product/machine (first-pass yield, rework rate, scrap rate)",
            "OEE trend data — is a machine degrading over time? (schedule preventive maintenance)",
        ],
        "aps_enrichment": (
            "When APS uses actual OEE data instead of standard times, schedule accuracy "
            "improves dramatically. A machine running at 85% performance doesn't produce "
            "what the standard says it should. Feeding OEE actuals into APS corrects "
            "this — the schedule reflects reality, not the spec sheet."
        ),
    },
    "historian_integration": {
        "purpose": (
            "Historians (OSIsoft PI, GE Proficy Historian, Canary Labs, AVEVA Historian) "
            "store time-series process data. APS can consume aggregated historian data "
            "for batch duration analysis, process variability quantification, and "
            "predictive scheduling."
        ),
        "use_cases": [
            "Analyzing actual batch durations to improve APS processing time estimates",
            "Identifying process variability patterns (e.g., batch times increase on third shift)",
            "Feeding actual furnace temperatures and ramp rates into heat treat scheduling",
            "Correlating environmental conditions with yield to optimize production windows",
        ],
    },
    "common_integration_failures": [
        {
            "failure": "Master data mismatch",
            "description": (
                "BOMs, routings, and resource definitions in ERP don't match reality. "
                "Setup times are wrong. Operation sequences are outdated. Work centers "
                "don't match physical resources. The APS optimizes against fiction."
            ),
            "frequency": "Extremely common — the #1 cause of APS implementation failure",
            "resolution": (
                "Master data cleansing project BEFORE APS go-live. Validate every "
                "routing, every setup time, every resource calendar against the shop "
                "floor. Budget 30-40% of implementation time for this."
            ),
        },
        {
            "failure": "One-way integration (push only, no feedback loop)",
            "description": (
                "APS pushes a schedule to the floor but never receives actuals back. "
                "The schedule diverges from reality within hours. Planners stop trusting "
                "the system and go back to spreadsheets."
            ),
            "frequency": "Very common in early/failed implementations",
            "resolution": (
                "Design bidirectional integration from day one. APS must consume actual "
                "production events (MES or manual feedback) to reschedule remaining work."
            ),
        },
        {
            "failure": "Over-integration (too much data, too frequently)",
            "description": (
                "Sending every machine event to APS in real time overwhelms the system. "
                "APS reschedules continuously, creating schedule instability ('schedule "
                "nervousness'). Planners see the schedule change every 5 minutes and "
                "lose confidence."
            ),
            "frequency": "Common in technically ambitious implementations",
            "resolution": (
                "Define a rescheduling cadence that balances responsiveness with stability. "
                "Most shops need 1-3 rescheduling cycles per shift, not continuous. "
                "Use exception-based triggers (machine down, quality hold) for ad-hoc "
                "rescheduling between cycles."
            ),
        },
        {
            "failure": "Ignoring the human feedback loop",
            "description": (
                "The schedule is generated by APS but planners/supervisors override it "
                "constantly because the system doesn't capture their tribal knowledge: "
                "operator preferences, machine quirks, customer priorities that aren't "
                "in the system."
            ),
            "frequency": "Nearly universal in early adoption",
            "resolution": (
                "Build a 'scheduler's workbench' — a UI where planners can see the APS "
                "schedule, drag-and-drop adjustments, and have those adjustments feed "
                "back into the model. Encode tribal knowledge as soft constraints. "
                "The goal is 'decision support,' not 'autopilot.'"
            ),
        },
        {
            "failure": "ERP upgrade breaks the integration",
            "description": (
                "ERP vendor releases an update that changes table structures, API "
                "schemas, or business logic. The APS integration breaks silently — "
                "data stops flowing or flows incorrectly."
            ),
            "frequency": "Periodic — every 6-18 months with cloud ERP",
            "resolution": (
                "Use an integration middleware layer (not point-to-point). Abstract the "
                "integration through a canonical data model. Include integration "
                "regression testing in the ERP upgrade validation plan."
            ),
        },
    ],
}


# ===========================================================================
# 4. KEY METRICS
# ===========================================================================

KEY_METRICS: Dict[str, Dict[str, Any]] = {
    "otd": {
        "name": "On-Time Delivery",
        "definition": (
            "Percentage of orders (or order lines) delivered on or before the customer-"
            "committed date. The single most important metric for customer-facing "
            "manufacturing performance."
        ),
        "calculation": "OTD% = (orders delivered on time / total orders due) x 100",
        "benchmarks": {
            "world_class": "98-99%+",
            "good": "95-97%",
            "average": "85-94%",
            "poor": "Below 85%",
        },
        "common_pitfalls": [
            "Measuring against 'scheduled ship date' instead of 'customer request date' (hides rescheduling to easier dates)",
            "Excluding partial shipments (shipping 80% of an order on time doesn't count if the customer needed 100%)",
            "Not tracking 'too early' — delivering weeks early creates inventory costs for the customer",
            "Aggregating across all customers instead of tracking per-customer (one large customer may mask failures to small ones)",
        ],
        "aps_impact": (
            "APS directly improves OTD by creating feasible schedules that account for "
            "actual capacity constraints and material availability. When the schedule is "
            "achievable, OTD improves because the plan matches reality."
        ),
    },
    "throughput": {
        "name": "Throughput",
        "definition": (
            "The rate at which the system produces finished goods. In TOC terms: "
            "throughput = revenue generated by the system per unit time. Not the same "
            "as output — throughput only counts what's sold, not what's made."
        ),
        "toc_formula": "Throughput = Revenue - Truly Variable Costs (materials, commissions, etc.)",
        "why_it_matters": (
            "Throughput is the primary metric in TOC because it's the only way to "
            "grow the business. Cutting costs has a floor (zero). Increasing throughput "
            "has no ceiling. APS increases throughput by maximizing the constraint's "
            "productive utilization."
        ),
    },
    "wip": {
        "name": "Work In Process",
        "definition": (
            "The total value (or quantity) of partially completed work on the shop floor. "
            "Includes raw materials released to production, parts in queue, parts being "
            "processed, and finished goods awaiting inspection/packaging."
        ),
        "littles_law": "WIP = Throughput x Cycle Time (reducing either reduces WIP)",
        "why_excess_wip_hurts": [
            "Ties up cash (working capital trapped on the floor)",
            "Increases lead times (more WIP = longer queues = longer wait times)",
            "Hides quality problems (defects are discovered further downstream)",
            "Complicates scheduling (more jobs to track = more complexity)",
            "Consumes floor space (staging areas fill up, creating physical constraints)",
        ],
        "aps_impact": (
            "APS reduces WIP by controlling work release (don't start jobs too early) "
            "and by creating schedules where operations are tightly sequenced. TOC's "
            "'rope' mechanism is specifically designed to control WIP by tying material "
            "release to constraint consumption."
        ),
    },
    "cycle_time": {
        "name": "Cycle Time (Manufacturing Lead Time)",
        "definition": (
            "Total elapsed time from work order release to completion. Includes "
            "processing time, queue time, move time, setup time, and wait time. "
            "In most shops, processing time is 5-15% of total cycle time — the rest "
            "is waiting."
        ),
        "components": {
            "processing_time": "Actual time the part is being worked on (value-added)",
            "queue_time": "Time spent waiting for a resource to become available (usually 60-80% of cycle time)",
            "setup_time": "Time to changeover the resource for this product",
            "move_time": "Time to transport between operations (usually negligible in a single plant)",
            "wait_time": "Time spent waiting for other reasons (material, quality hold, batch accumulation)",
        },
        "aps_impact": (
            "APS reduces cycle time primarily by reducing queue time — scheduling "
            "operations to start when the resource is available, rather than releasing "
            "work and letting it pile up. A 30% reduction in cycle time is common in "
            "the first year of APS implementation."
        ),
    },
    "changeover_time": {
        "name": "Changeover / Setup Time",
        "definition": (
            "Time from the last good unit of the previous product to the first good "
            "unit of the next product. Includes teardown, preparation, adjustment, "
            "and first-article inspection."
        ),
        "why_it_matters": (
            "Every minute of changeover is a minute of lost production on the resource. "
            "On a bottleneck, changeover time directly reduces throughput. APS can "
            "optimize sequencing to minimize total changeover time (light-to-dark, "
            "same-family batching, etc.) even without physically reducing changeover "
            "duration."
        ),
        "relationship_to_batch_size": (
            "Long changeovers incentivize large batches (amortize the setup over more "
            "units). But large batches increase inventory and reduce flexibility. SMED "
            "reduces changeover time, enabling smaller batches. APS quantifies the "
            "trade-off and finds the optimal balance."
        ),
    },
    "oee": {
        "name": "Overall Equipment Effectiveness",
        "formula": "OEE = Availability x Performance x Quality",
        "components": {
            "availability": (
                "Actual running time / planned production time. Losses: breakdowns, "
                "changeovers, material shortages, operator absence."
            ),
            "performance": (
                "Actual output / theoretical output at standard cycle time. Losses: "
                "slow cycles, minor stops, idling."
            ),
            "quality": (
                "Good units / total units produced. Losses: scrap, rework, startup "
                "rejects."
            ),
        },
        "benchmarks": {
            "world_class": "85%+ (but highly industry-dependent)",
            "typical_discrete": "60-75%",
            "typical_process": "70-85%",
            "poor": "Below 50% (but common in plants that don't measure it)",
        },
        "aps_interaction": (
            "APS and OEE form a feedback loop. OEE data feeds into APS as actual "
            "performance parameters (real cycle times, real downtime patterns, real "
            "quality yields). APS uses this data to create more accurate schedules. "
            "Better schedules improve availability (fewer changeovers, better "
            "sequencing). Better availability improves OEE."
        ),
    },
    "schedule_adherence": {
        "name": "Schedule Adherence / Schedule Attainment",
        "definition": (
            "Percentage of scheduled operations that were executed as planned "
            "(on the planned resource, at the planned time, in the planned quantity). "
            "Measures how well the shop floor executes the schedule."
        ),
        "calculation": "Schedule Adherence% = (operations completed as scheduled / total scheduled operations) x 100",
        "why_it_matters": (
            "If schedule adherence is below 70%, the schedule is effectively a "
            "suggestion, not a plan. Either the schedule isn't feasible (APS problem) "
            "or the shop floor isn't executing (discipline/culture problem). Improving "
            "adherence requires addressing both."
        ),
        "target": "85-95% is realistic for most discrete manufacturing",
    },
    "capacity_utilization": {
        "name": "Capacity Utilization",
        "definition": (
            "Actual output / maximum possible output (at rated capacity). "
            "Measures how much of available capacity is being used."
        ),
        "nuance": (
            "100% utilization is NOT the goal. TOC teaches that non-bottleneck "
            "resources should have protective capacity (idle time that allows them "
            "to catch up after variability events). Only the bottleneck should be "
            "targeted for maximum utilization. Running every resource at 100% "
            "guarantees high WIP and long lead times."
        ),
    },
    "takt_time": {
        "name": "Takt Time",
        "definition": (
            "Available production time per period / customer demand per period. "
            "The pace at which production must run to match customer demand. "
            "Derived from demand, not from production capability."
        ),
        "calculation": "Takt = (available minutes per shift x shifts per day) / daily demand",
        "example": (
            "If a customer needs 480 units per day and you have 480 available minutes "
            "per day, takt time is 1 minute per unit. Every operation must complete "
            "within 1 minute."
        ),
        "aps_relevance": (
            "In flow/line environments, APS uses takt time to balance operations "
            "across workstations and identify where takt is violated. In mixed-model "
            "lines, takt varies by model variant — the schedule must sequence models "
            "to smooth the takt variation."
        ),
    },
}


# ===========================================================================
# 5. COMMON OBJECTIONS AND REAL ANSWERS
# ===========================================================================

COMMON_OBJECTIONS: List[Dict[str, Any]] = [
    {
        "objection": "We already have scheduling in our ERP",
        "who_says_it": "IT leaders, ERP project managers, CFOs who invested heavily in ERP",
        "what_they_really_mean": (
            "We spent $5M on this ERP and I can't justify another system. Also, I "
            "don't understand why ERP scheduling isn't sufficient."
        ),
        "the_real_answer": (
            "ERP scheduling (MRP) uses infinite capacity by default. It generates "
            "planned orders based on demand and lead times without checking whether "
            "your resources can actually handle the load. The result is an overloaded "
            "schedule that your planners manually deconflict in spreadsheets every "
            "morning.\n\n"
            "APS doesn't replace your ERP — it sits on top of it. It consumes demand "
            "and master data from ERP, creates a finite-capacity schedule that respects "
            "your actual constraints, and writes the schedule back to ERP for execution. "
            "Your ERP investment is preserved and enhanced.\n\n"
            "The test: ask your planners if they trust the MRP dates. If they're "
            "adjusting them daily, that's the gap APS fills."
        ),
        "proof_points": [
            "MRP was designed in the 1970s for infinite-capacity planning — it was never intended for shop floor scheduling",
            "Even SAP's own documentation recommends third-party APS for finite-capacity scheduling",
            "ERP planned order dates are typically overridden by planners within 24 hours of generation",
        ],
    },
    {
        "objection": "Our planners use Excel and it works fine",
        "who_says_it": "Plant managers, lead schedulers who built the spreadsheets, controllers",
        "what_they_really_mean": (
            "Our best planner has 20 years of knowledge in their head and a spreadsheet "
            "that sort of captures it. It 'works' in the sense that we ship product. "
            "But I'm also terrified of what happens when that person retires."
        ),
        "the_real_answer": (
            "If it works, respect that — it means you have skilled planners who "
            "understand your constraints. The question isn't whether Excel works today. "
            "It's three other questions:\n\n"
            "1. What happens when your best planner is sick, on vacation, or leaves? "
            "That spreadsheet is tribal knowledge in a file. If the person who built it "
            "walks out, can anyone else use it?\n\n"
            "2. How long does replanning take? When a machine goes down or a priority "
            "changes, how long does it take to rebuild the schedule? In Excel, it's "
            "hours. In APS, it's minutes.\n\n"
            "3. How do you know if it's optimal? Excel can tell you 'this works.' It "
            "can't tell you 'this is the best possible sequence for throughput and "
            "on-time delivery.' You might be leaving 10-20% capacity on the table and "
            "not know it.\n\n"
            "APS doesn't replace your planner's knowledge — it captures and amplifies "
            "it. The planner's expertise becomes the constraints and rules in the system, "
            "not locked in one person's head."
        ),
        "proof_points": [
            "Average age of manufacturing planners in the US is 55+ — retirement wave is real",
            "Excel cannot model sequence-dependent setups, finite capacity, or multi-constraint optimization",
            "One APS customer found they had 18% more usable capacity once they stopped scheduling in Excel",
        ],
    },
    {
        "objection": "We tried APS before and it failed",
        "who_says_it": "VP Operations, plant managers, IT directors who lived through the failed project",
        "what_they_really_mean": (
            "We spent $300K-$1M, suffered through a painful implementation, and the "
            "planners went back to spreadsheets within 6 months. I have scar tissue "
            "and zero appetite for doing that again."
        ),
        "the_real_answer": (
            "Fair. And we should talk about why it failed, because the failure pattern "
            "is almost always the same — and it's not usually the software.\n\n"
            "The three most common reasons APS implementations fail:\n\n"
            "1. Master data quality: The routings, setup times, and resource calendars "
            "in ERP didn't match reality. The APS optimized against fiction. Every "
            "schedule it produced was wrong, and planners lost trust within weeks.\n\n"
            "2. Big bang go-live: The vendor tried to schedule the entire plant on "
            "day one. Too much complexity, too many data issues surfacing simultaneously, "
            "no time to learn. Should have started with one line, one constraint, one "
            "win — then expanded.\n\n"
            "3. No feedback loop: The APS pushed a schedule but never received actuals "
            "back. Within hours, the schedule diverged from reality. By afternoon, it "
            "was useless.\n\n"
            "A second attempt succeeds when you fix these three things first. And the "
            "cost of fixing them is a fraction of the cost of living without "
            "finite-capacity scheduling."
        ),
        "proof_points": [
            "80%+ of APS failures are attributed to master data quality and change management, not software",
            "Phased implementations (start with bottleneck, expand) have 3x higher adoption rates",
            "Second-attempt implementations succeed at 85%+ rates because lessons from the first attempt are known",
        ],
    },
    {
        "objection": "Our shop floor is too variable for any plan",
        "who_says_it": "Production supervisors, shift leads, experienced operators",
        "what_they_really_mean": (
            "I deal with machine breakdowns, absenteeism, material shortages, rush "
            "orders, and quality issues every single day. No plan survives first "
            "contact with my shop floor. Why would I trust a computer to plan "
            "something this chaotic?"
        ),
        "the_real_answer": (
            "Variability is not an argument against planning. It's the argument FOR "
            "better planning.\n\n"
            "In a perfectly stable environment, you don't need APS — a static schedule "
            "in Excel would work forever. It's precisely BECAUSE your floor is variable "
            "that you need a system that can:\n\n"
            "- Absorb disruptions and reschedule in minutes, not hours\n"
            "- Buffer the constraint against variability (TOC time buffers)\n"
            "- Show you the downstream impact of a disruption before you make a decision\n"
            "- Run what-if scenarios: 'if Machine 7 is down until 2pm, what ships late?'\n\n"
            "The goal isn't a perfect plan. The goal is a plan that degrades "
            "gracefully — one that tells you exactly what's at risk and what the "
            "best recovery option is. That's what constraint-aware scheduling does."
        ),
        "proof_points": [
            "Plants with high variability see the LARGEST improvements from APS — 25-40% cycle time reduction",
            "Time to replan after a disruption goes from hours (Excel) to minutes (APS)",
            "What-if scenarios let supervisors evaluate options before committing — reducing firefighting by 50%+",
        ],
    },
    {
        "objection": "We can't afford the downtime for implementation",
        "who_says_it": "Plant managers, operations VPs, CFOs",
        "what_they_really_mean": (
            "We're already running at full capacity and behind on orders. I can't "
            "spare my planners for training and data cleanup. And if the new system "
            "causes a scheduling gap, we'll miss shipments."
        ),
        "the_real_answer": (
            "A well-run APS implementation doesn't require production downtime. Here's "
            "why:\n\n"
            "1. APS runs in parallel during implementation. Your current process "
            "continues unchanged. The APS is configured, tested, and validated against "
            "your actual production data — in shadow mode — before anyone switches.\n\n"
            "2. We start with one area, not the whole plant. Pick your biggest "
            "constraint — the work center that causes the most pain. Implement APS "
            "there first. Prove value in 90 days. Then expand.\n\n"
            "3. The real cost isn't the implementation — it's the status quo. Every "
            "day without finite-capacity scheduling, you're leaving capacity on the "
            "table, expediting unnecessarily, carrying excess WIP, and missing "
            "delivery dates. That has a cost. We can help you quantify it.\n\n"
            "4. Planner time investment is real but bounded: typically 2-4 hours per "
            "week during the 90-day implementation phase for the primary planner. "
            "That's the cost of teaching the system what the planner already knows."
        ),
        "proof_points": [
            "90-day time-to-first-value implementation target — not a multi-year project",
            "Parallel (shadow mode) implementation means zero disruption to current operations",
            "Typical planner time commitment: 2-4 hours/week for 90 days — less than they spend replanning in Excel",
        ],
    },
    {
        "objection": "Our people won't adopt it",
        "who_says_it": "Plant managers, HR, change-averse organizations",
        "what_they_really_mean": (
            "We've rolled out systems before and people resisted. Our planners like "
            "their way of doing things. I'm worried we'll spend the money and nobody "
            "will use it."
        ),
        "the_real_answer": (
            "Adoption fails when the system makes the planner's job harder, not easier. "
            "If the APS produces schedules the planner has to fight with, they'll go "
            "back to their spreadsheet — and they should.\n\n"
            "Adoption succeeds when:\n"
            "- The planner's tribal knowledge is encoded in the system (not overridden by it)\n"
            "- The planner can override the system when they know better (and the system learns from the override)\n"
            "- The schedule the system produces is better than what the planner could do manually (provably, not theoretically)\n"
            "- Replanning after a disruption takes 5 minutes instead of 2 hours\n\n"
            "The best predictor of adoption is whether the scheduler says 'this makes "
            "my life easier' within the first two weeks. Our implementation methodology "
            "starts with the scheduler's workflow, not the software's features."
        ),
        "proof_points": [
            "Implementations that start with planner workflow mapping have 80%+ adoption within 90 days",
            "Planner override capability is non-negotiable — the system advises, the planner decides",
            "When replanning time drops from hours to minutes, adoption follows naturally",
        ],
    },
    {
        "objection": "We need to fix our ERP data first",
        "who_says_it": "IT leaders, ERP administrators, consultants",
        "what_they_really_mean": (
            "Our master data is a mess — routings are outdated, BOMs are inaccurate, "
            "and work center calendars don't reflect reality. We feel like we need to "
            "clean all of that up before we can even think about APS."
        ),
        "the_real_answer": (
            "You're partly right and partly wrong. You DO need accurate master data "
            "for APS to work. But you DON'T need to fix all of it upfront.\n\n"
            "The approach that works:\n"
            "1. Pick one area (your constraint work center and its immediate upstream/downstream)\n"
            "2. Validate and correct master data for THAT area only (routings, setup times, calendars)\n"
            "3. Implement APS for that area\n"
            "4. As you expand, clean data for each new area\n\n"
            "Trying to fix all master data before starting APS is a project that never "
            "ends — there will always be more data to clean. Starting with a focused "
            "area gives you a forcing function: the APS immediately exposes incorrect "
            "data because the schedule won't match reality. This actually accelerates "
            "data quality improvement because there's a real consequence for bad data."
        ),
        "proof_points": [
            "Focused data cleanup for one area takes 2-4 weeks, not 6-12 months",
            "APS exposes master data errors faster than any audit — if the schedule is wrong, the data is wrong",
            "Plants that use APS as a data quality forcing function reach 95%+ data accuracy within 6 months",
        ],
    },
]


# ===========================================================================
# 6. SCHEDULING MATURITY MODEL
# ===========================================================================

MATURITY_MODEL: Dict[str, Any] = {
    "overview": (
        "Most manufacturers are at Level 1-2 of scheduling maturity. They know it. "
        "They feel the pain daily — firefighting, replanning, missed deliveries, "
        "excess inventory. The maturity model helps them see where they are, where "
        "they need to be, and what the path looks like."
    ),
    "levels": [
        {
            "level": 0,
            "name": "Tribal / Ad Hoc",
            "description": (
                "Scheduling is in people's heads. The lead scheduler or supervisor "
                "decides what to run based on experience, instinct, and whoever yells "
                "loudest. No formal system. No documented plan."
            ),
            "characteristics": [
                "Schedule exists only in the head of 1-2 people",
                "Priority determined by who asks loudest or most recently",
                "No visibility into future capacity or conflicts",
                "Reactive firefighting is the default operating mode",
                "No concept of finite capacity — 'just fit it in'",
            ],
            "symptoms": [
                "When the lead scheduler is out, nobody knows what to run next",
                "Every order is treated as 'hot' or 'urgent'",
                "Overtime is constant and unplanned",
                "No ability to give customers reliable delivery dates",
            ],
            "prevalence": "15-20% of small manufacturers (<$20M revenue)",
        },
        {
            "level": 1,
            "name": "Spreadsheet / Manual",
            "description": (
                "Scheduling is done in Excel or Google Sheets. The planner has built "
                "a workbook that captures key jobs, resources, and dates. It works "
                "but is fragile, manual, and person-dependent."
            ),
            "characteristics": [
                "Excel/Sheets-based planning board (Gantt-like or list-based)",
                "Manual data entry from ERP printouts or reports",
                "Planner is the 'human APS' — they hold the logic in their head, Excel holds the data",
                "Replanning after a disruption takes 2-4 hours",
                "No automated constraint checking",
                "Version control issues — 'which version of the schedule is current?'",
            ],
            "symptoms": [
                "The scheduler's laptop is the most critical asset in the plant",
                "Nobody else can read or update the spreadsheet",
                "'What-if' analysis means the planner stares at the ceiling and thinks",
                "Schedule is published once per day (or less) and is stale by midmorning",
            ],
            "prevalence": "40-50% of manufacturers (the single largest group)",
        },
        {
            "level": 2,
            "name": "Basic MRP / ERP Planning",
            "description": (
                "Using MRP module in ERP for planning. Planned orders are generated "
                "based on demand, BOMs, and lead times. But scheduling is still "
                "infinite-capacity, and planners manually adjust the MRP output."
            ),
            "characteristics": [
                "MRP generates planned orders with start/end dates",
                "Planners export MRP output and manually adjust for capacity",
                "Capacity planning is rough-cut (RCCP) at best",
                "No sequence-dependent setup optimization",
                "Limited visibility into constraint impact",
                "Planners maintain a shadow spreadsheet for the 'real' schedule",
            ],
            "symptoms": [
                "MRP dates are treated as suggestions — planners override 50-80% of them",
                "Capacity overload reports show red on every work center every week",
                "The gap between MRP plan and actual execution grows throughout the week",
                "Planners spend more time fixing MRP output than using it",
            ],
            "prevalence": "25-30% of manufacturers",
        },
        {
            "level": 3,
            "name": "Finite Capacity Scheduling",
            "description": (
                "APS system in use for finite-capacity scheduling. The schedule respects "
                "resource constraints, models sequence-dependent setups, and is connected "
                "to ERP for demand and master data."
            ),
            "characteristics": [
                "Dedicated APS tool generating finite-capacity schedules",
                "Bidirectional ERP integration (demand in, schedule out)",
                "Sequence-dependent setup optimization",
                "What-if scenario capability",
                "Visual scheduling board (Gantt) with drag-and-drop adjustment",
                "Replanning after disruptions in minutes, not hours",
                "Planners trust the schedule and execute from it",
            ],
            "symptoms_of_success": [
                "OTD improves 10-25% within first 6 months",
                "WIP decreases as work release is controlled",
                "Planners shift from firefighting to forward-looking decision-making",
                "The schedule is published multiple times per day and remains accurate",
            ],
            "prevalence": "8-12% of manufacturers",
        },
        {
            "level": 4,
            "name": "Constraint-Aware / Integrated",
            "description": (
                "APS is connected to MES and OEE for real-time feedback. The schedule "
                "is informed by actual production performance, not just standards. "
                "Multiple constraint types are modeled (equipment, labor, materials, "
                "quality, regulatory). TOC principles are applied."
            ),
            "characteristics": [
                "APS + MES + OEE integration (closed-loop scheduling)",
                "Real-time actual performance data feeding APS (actual cycle times, actual yields, actual downtime)",
                "Multi-constraint modeling (equipment + labor + materials + quality + regulatory)",
                "TOC / DBR methodology applied to constraint management",
                "Buffer management with green/yellow/red status tracking",
                "Cross-plant scheduling for multi-site operations",
                "Advanced analytics on schedule performance (adherence, root cause of misses)",
            ],
            "symptoms_of_success": [
                "OTD consistently above 95%",
                "Cycle times reduced 25-40% from pre-APS baseline",
                "Planners are strategic — managing constraints, not managing spreadsheets",
                "The schedule drives the floor, not the other way around",
            ],
            "prevalence": "3-5% of manufacturers",
        },
        {
            "level": 5,
            "name": "Predictive / Autonomous",
            "description": (
                "AI/ML models augment scheduling decisions: predicting disruptions "
                "before they occur, recommending optimal sequences based on historical "
                "performance, automatically adjusting schedules based on real-time events. "
                "The planner supervises; the system proposes."
            ),
            "characteristics": [
                "Predictive maintenance integration — schedule around predicted failures",
                "ML-optimized sequencing based on historical performance data",
                "Automatic rescheduling triggered by real-time events (machine down, quality hold)",
                "Digital twin of the production system for simulation and scenario planning",
                "Self-tuning processing times and yield factors based on actual performance",
                "Demand sensing / demand shaping integration",
                "Autonomous replanning within planner-defined guardrails",
            ],
            "symptoms_of_success": [
                "OTD above 98% consistently",
                "Proactive disruption avoidance rather than reactive recovery",
                "Schedule adherence above 95%",
                "Continuous improvement loop: system learns from every disruption and adapts",
            ],
            "prevalence": "Less than 1% of manufacturers (aspirational for most)",
        },
    ],
    "key_insight": (
        "The gap between Level 1 (spreadsheet) and Level 3 (finite capacity) is where "
        "most value is created. Moving from Level 1 to Level 3 typically delivers "
        "15-30% OTD improvement, 20-40% cycle time reduction, and 10-25% WIP "
        "reduction. The path from Level 3 to Level 5 is incremental improvement. "
        "Don't let aspirations for Level 5 prevent action at Level 3."
    ),
    "where_most_manufacturers_are": (
        "Approximately 55-70% of manufacturers are at Level 0-1 (tribal or spreadsheet). "
        "Another 25-30% are at Level 2 (basic MRP). Only 10-15% have achieved Level 3+. "
        "The primary market for APS implementation is the Level 1-2 population that "
        "knows they need something better but doesn't know what or how."
    ),
}


# ===========================================================================
# 7. REAL OPERATIONAL LANGUAGE
# ===========================================================================

OPERATIONAL_LANGUAGE: Dict[str, Any] = {
    "overview": (
        "How people in manufacturing operations actually talk about scheduling — "
        "by role, by frustration, by vocabulary. This is NOT marketing language. "
        "This is what you'd hear on the plant floor, in the scheduling meeting, "
        "and in the boardroom."
    ),
    "by_role": {
        "plant_scheduler_planner": {
            "title_variations": [
                "Production Scheduler",
                "Master Scheduler",
                "Production Planner",
                "Planning Analyst",
                "Material Planner",
                "Scheduling Coordinator",
            ],
            "daily_reality": (
                "Arrives at 5:30-6:00 AM. Checks what ran overnight. Checks what didn't "
                "run. Checks what broke. Rebuilds the schedule based on what actually "
                "happened versus what was supposed to happen. Spends the morning "
                "firefighting: answering 'when will my order ship?' calls, juggling "
                "priorities, arguing with production about what to run next. By "
                "afternoon, the schedule they built in the morning is already wrong."
            ),
            "phrases_they_use": [
                "The schedule looked good at 6 AM. By 10, everything shifted.",
                "I'm just trying to keep the hot list from growing.",
                "If I could just get maintenance to tell me BEFORE the machine goes down...",
                "I have 200 jobs and 6 machines. You do the math.",
                "MRP says start all of these Monday. Where? On what?",
                "I know which jobs are late. I need to know which ones are about to be.",
                "Don't give me another tool — give me one that actually works with our data.",
                "My whole job is managing exceptions to the plan.",
                "The plan isn't wrong. Reality is just... different.",
                "I've been doing this for 25 years. I know the constraints. I just can't show them to anyone.",
                "We replan every Wednesday. Sometimes Tuesday.",
                "Half my day is answering 'where's my order' emails.",
                "I can't go on vacation. Last time I did, the schedule fell apart in two days.",
                "Setup time is killing us. We're changing over 6 times on a 4-hour run.",
            ],
            "what_frustrates_them": [
                "Systems that don't reflect reality (wrong setup times, missing constraints)",
                "Being blamed when orders are late even though capacity was overloaded from the start",
                "No visibility into what's coming — surprises from sales, engineering changes, material delays",
                "Having to maintain a 'shadow schedule' in Excel because the official system doesn't work",
                "Being the single point of failure — nobody else can do their job",
                "Sales promising delivery dates without checking capacity",
            ],
            "what_they_secretly_want": [
                "A system that thinks the way they think — not the way an ERP vendor thinks they should",
                "To be able to show leadership WHY orders are late (capacity proof, not excuses)",
                "To replan in 5 minutes when something goes wrong, not 3 hours",
                "To go on vacation without worrying the plant will fall apart",
                "To be recognized as the strategic asset they are, not 'the person who fills in the spreadsheet'",
                "To stop being a firefighter and start being a decision-maker",
            ],
        },
        "production_supervisor_shift_lead": {
            "title_variations": [
                "Production Supervisor",
                "Shift Supervisor",
                "Shift Lead",
                "Area Lead",
                "Production Lead",
                "Floor Supervisor",
            ],
            "daily_reality": (
                "Manages the hour-by-hour execution of the schedule. Deals with "
                "machine issues, operator issues, quality issues, and material issues "
                "in real time. Often overrides the schedule based on immediate "
                "shop-floor conditions."
            ),
            "phrases_they_use": [
                "I don't care what the schedule says — Machine 4 is down.",
                "We need to run this job next because the material is about to expire.",
                "I moved the setup to second shift because we didn't have the operator.",
                "The schedule says 3 hours. It's going to take 5. Trust me.",
                "Nobody told me we were changing the priority.",
                "I need parts from upstream and they're not here.",
                "We're making chips, not schedules. Things happen.",
                "Give me a schedule I can actually run, not a wish list.",
            ],
            "what_frustrates_them": [
                "Receiving a schedule that's impossible with current staffing/equipment status",
                "Schedule changes multiple times per shift without explanation",
                "Being expected to hit targets when the plan is already broken",
                "No input into the schedule — decisions made in an office that don't match floor reality",
            ],
        },
        "vp_operations_coo": {
            "title_variations": [
                "VP of Operations",
                "VP of Manufacturing",
                "COO",
                "SVP Operations",
                "Director of Operations",
                "General Manager (plant-level)",
            ],
            "strategic_view": (
                "Cares about the big picture: on-time delivery, throughput, cost per "
                "unit, capacity utilization, and customer satisfaction. Doesn't look at "
                "individual jobs — looks at trends, KPIs, and whether the operation can "
                "support growth."
            ),
            "phrases_they_use": [
                "Our on-time delivery is at 82% and the board wants 95%. What do I need?",
                "We're adding $10M in new business. Can we handle it without capital expansion?",
                "I need to know our real capacity — not nameplate, not theoretical. Real.",
                "Why are we constantly expediting? What's the root cause?",
                "We have $4M in WIP on the floor. Where is it and why is it stuck?",
                "I can't make capital investment decisions without understanding our constraint.",
                "Our competitors are quoting 4-week lead times. We're at 8. Why?",
                "Show me the data. I don't want anecdotes — I want a capacity model.",
                "Every month we miss deliveries, have the same root causes, and nothing changes.",
                "I need scheduling to be a process, not a person.",
                "If we lose our scheduler, we lose the business. That's unacceptable.",
            ],
            "what_they_care_about": [
                "OTD as a customer satisfaction and revenue retention metric",
                "Capacity planning for growth — can we take new business without new machines?",
                "Working capital tied up in WIP and finished goods inventory",
                "Cost of poor scheduling: overtime, premium freight, expediting, excess inventory",
                "Risk reduction: key-person dependency on the scheduler",
                "Data-driven decision-making: replacing gut feel with models",
                "Competitive lead time and responsiveness",
            ],
            "how_they_evaluate_aps": [
                "ROI within 12 months (hard savings: reduced overtime, premium freight, inventory)",
                "Implementation risk and timeline (will it disrupt current operations?)",
                "Adoption likelihood (will my people actually use it?)",
                "Scalability (will it work as we grow? Across multiple plants?)",
                "Vendor viability and support model (will the vendor be around in 5 years?)",
            ],
        },
        "supply_chain_director": {
            "title_variations": [
                "VP Supply Chain",
                "Director of Supply Chain",
                "Supply Chain Manager",
                "Director of Planning",
                "S&OP Manager",
            ],
            "strategic_view": (
                "Sits at the intersection of demand, supply, and production. Needs "
                "planning and execution to be connected. Frustrated by the gap between "
                "the demand plan and what actually gets produced."
            ),
            "phrases_they_use": [
                "The forecast says one thing. The production plan says another. The floor does a third.",
                "I need to run S&OP with real capacity data, not guesses.",
                "Our safety stock is through the roof because we can't trust production dates.",
                "Supplier lead times are unpredictable and our planning can't absorb the variability.",
                "I need ATP/CTP that reflects actual capacity, not infinite-capacity MRP dates.",
                "We're carrying 12 weeks of inventory because we can't trust the schedule.",
            ],
        },
        "it_ot_stakeholder": {
            "title_variations": [
                "IT Director (Manufacturing)",
                "OT Manager",
                "Systems Architect",
                "Manufacturing Systems Manager",
                "Digital Transformation Lead",
            ],
            "strategic_view": (
                "Responsible for the technology stack. Worried about integration "
                "complexity, data architecture, system maintainability, and not adding "
                "yet another siloed application."
            ),
            "phrases_they_use": [
                "How does this connect to our ERP? To our MES? To our historian?",
                "I've seen too many point solutions create data silos.",
                "Where does this sit in our ISA-95 architecture?",
                "Who maintains this after go-live? My team is already stretched.",
                "If the vendor disappears, are we locked in?",
                "We just migrated to cloud ERP. Will this survive the next upgrade?",
                "API-first or it's a non-starter.",
                "I need an integration pattern I can maintain, not a custom nightmare.",
            ],
        },
    },
    "universal_frustrations": {
        "description": (
            "Things that EVERYONE in manufacturing says about scheduling, regardless "
            "of role. These are the shared pain points that resonate across the organization."
        ),
        "phrases": [
            "The plan never survives Monday.",
            "We're always firefighting.",
            "We make great product. We just can't tell you when it'll be done.",
            "Our customers are losing patience with our lead times.",
            "We have the capacity. We just can't use it effectively.",
            "Everything is 'hot.' When everything is a priority, nothing is.",
            "We're scheduling in the dark.",
            "I don't know where my order is.",
            "We keep adding overtime but output isn't increasing.",
            "The same problems come up every month and nothing changes.",
            "We're not out of capacity. We're out of visibility.",
        ],
    },
    "vocabulary_guide": {
        "description": (
            "Words and phrases that manufacturing operations people use naturally. "
            "Using this vocabulary in marketing content signals credibility. Using "
            "the wrong vocabulary signals 'this person has never set foot in a plant.'"
        ),
        "use_these": {
            "scheduling_terms": [
                "constraint",
                "bottleneck",
                "binding constraint",
                "capacity",
                "finite capacity",
                "changeover / setup",
                "sequence / sequencing",
                "dispatch / dispatch list",
                "work order / job / shop order",
                "routing / work center / operation",
                "lead time (manufacturing vs. procurement)",
                "cycle time",
                "queue time",
                "WIP (work in process)",
                "throughput",
                "flow",
                "pull / push",
                "release (work release, order release)",
                "backlog / past-due",
                "hot list / expedite list",
                "replan / reschedule",
                "what-if / scenario",
            ],
            "operational_terms": [
                "shop floor / floor",
                "work center",
                "run rate",
                "uptime / downtime",
                "scrap / rework / yield",
                "first-pass yield",
                "machine down / breakdown",
                "planned maintenance / PM",
                "shift (first/second/third, day/swing/grave)",
                "overtime / OT",
                "standard time / actual time",
                "material availability / stock-out",
                "kit / kitting",
                "staging area",
                "lot / batch",
                "campaign",
            ],
            "business_terms": [
                "on-time delivery / OTD",
                "service level",
                "customer promise date / commit date",
                "available-to-promise / ATP",
                "capable-to-promise / CTP",
                "order-to-ship / order-to-delivery",
                "cost of poor quality / COPQ",
                "premium freight",
                "inventory carrying cost",
                "working capital",
                "capacity investment / capital expansion",
            ],
        },
        "avoid_these": {
            "description": (
                "Words and phrases that sound like marketing or IT, not manufacturing. "
                "Using these signals inauthenticity to an operations audience."
            ),
            "terms": [
                "synergy",
                "paradigm shift",
                "disruptive innovation",
                "bleeding edge",
                "game-changer",
                "robust solution",
                "best-in-class (without proof)",
                "seamless integration (nothing is seamless)",
                "turnkey solution",
                "unlock value",
                "leverage (as a verb for anything other than a lever)",
                "ecosystem (unless you're talking about biology)",
                "holistic approach",
                "empower / empowerment",
                "next-generation",
                "state-of-the-art",
                "world-class (unless backed by a specific benchmark)",
                "end-to-end visibility (unless you can describe exactly what that means)",
            ],
        },
    },
    "conversation_patterns": {
        "description": (
            "How scheduling conversations actually flow in discovery calls, "
            "plant visits, and S&OP meetings."
        ),
        "discovery_call_opener": (
            "The most effective opening question in an APS discovery call:\n"
            "'Walk me through what happens to your schedule between Monday and Wednesday.'\n\n"
            "This opens up the real pain without leading the witness. Every scheduler "
            "has a 'Wednesday story.' The answer reveals their constraint, their "
            "replanning process, and their frustration level — all in 2 minutes."
        ),
        "plant_walk_observations": [
            "WIP piles between work centers = queue time problem = scheduling opportunity",
            "Whiteboards with handwritten job lists = the 'real' schedule lives here, not in the system",
            "Color-coded stickers on jobs = priority override system the planners invented",
            "Operators idle while machines are loaded = labor-machine synchronization problem",
            "Fork trucks constantly moving = excess material movement from poor staging",
            "Expeditor with a walkie-talkie = full-time job that shouldn't need to exist",
        ],
        "red_flags_in_ops_reviews": [
            "'We track OTD to rescheduled date, not original promise date' — hiding poor performance",
            "'Our capacity utilization is 95%' — either not true or about to have quality/delivery problems",
            "'We don't have a bottleneck' — means they haven't looked, not that one doesn't exist",
            "'Our ERP handles scheduling' — means planners are working around it in Excel",
            "'We need more capacity' — often means they need better scheduling, not more machines",
        ],
    },
}


# ===========================================================================
# 8. SUPPORTING REFERENCE DATA
# ===========================================================================

APS_VENDOR_LANDSCAPE: Dict[str, Any] = {
    "overview": (
        "The APS market is fragmented. No single vendor dominates all segments. "
        "Selection depends on industry, ERP platform, plant complexity, and budget. "
        "A vendor-agnostic approach is essential because the right APS depends on "
        "the manufacturer's specific environment."
    ),
    "market_segments": {
        "enterprise_planning_suites": {
            "description": "Broad supply chain planning platforms that include APS functionality",
            "vendors": [
                "Kinaxis Maestro (RapidResponse) — concurrent planning, strong S&OP through detailed scheduling",
                "SAP IBP / APO — SAP-native, best for SAP-heavy environments",
                "Oracle ASCP / Planning Cloud — Oracle-native planning",
                "Blue Yonder (JDA) — strong in retail/CPG supply chain",
                "o9 Solutions — AI-native planning platform",
            ],
        },
        "dedicated_aps_tools": {
            "description": "Purpose-built finite capacity scheduling tools for plant-level optimization",
            "vendors": [
                "Siemens Opcenter APS (Preactor) — strong in discrete manufacturing, wide industry coverage",
                "Dassault DELMIA Ortems — strong in process and hybrid manufacturing",
                "PlanetTogether — mid-market focused, strong in food/bev and CPG",
                "Optessa (Eyelit Technologies) — automotive and complex assembly sequencing",
                "Asprova — strong in Japan and automotive",
                "DELMIA Quintiq — large-scale resource planning and scheduling",
            ],
        },
        "niche_industry_tools": {
            "description": "APS tools built for specific industry verticals",
            "vendors": [
                "Greycon — paper, board, metals, converting industries",
                "GE ROB-EX — discrete manufacturing scheduling",
                "Infor Thru-Put — constraint-based scheduling aligned with TOC",
                "Simio — simulation-based scheduling for complex environments",
            ],
        },
    },
    "selection_criteria": [
        "Industry fit — does the vendor have proven deployments in your vertical?",
        "ERP compatibility — pre-built connectors for your specific ERP version?",
        "Constraint modeling depth — can it model YOUR specific constraints (not just generic ones)?",
        "Scalability — number of resources, operations, and planning horizon it can handle",
        "User interface — will your planners actually use it? Is the Gantt intuitive?",
        "What-if capability — can planners compare scenarios before committing?",
        "Implementation partner ecosystem — who will implement it and support it long-term?",
        "Total cost of ownership — license, implementation, annual maintenance, upgrade path",
    ],
}

ROI_FRAMEWORK: Dict[str, Any] = {
    "overview": (
        "The ROI case for APS is built on hard, measurable savings — not soft "
        "benefits. Every item below can be quantified from existing operational data."
    ),
    "savings_categories": {
        "reduced_overtime": {
            "description": "Better scheduling reduces unplanned overtime by 20-40%",
            "how_to_quantify": (
                "Current overtime hours x overtime premium rate x estimated reduction %. "
                "A plant spending $500K/year on overtime can typically save $100-200K."
            ),
        },
        "reduced_premium_freight": {
            "description": "Better OTD reduces emergency shipments by 30-60%",
            "how_to_quantify": (
                "Current premium freight spend x estimated reduction %. "
                "Automotive suppliers often spend $200K-$1M/year on premium freight."
            ),
        },
        "reduced_wip_inventory": {
            "description": "Controlled work release reduces WIP by 15-30%",
            "how_to_quantify": (
                "Current WIP value x carrying cost rate (typically 20-30% per year) x "
                "estimated WIP reduction %. A plant with $5M in WIP can free $250K-450K "
                "in working capital annually."
            ),
        },
        "reduced_changeover_waste": {
            "description": "Optimized sequencing reduces changeover frequency and startup scrap",
            "how_to_quantify": (
                "Number of changeovers per week x (average changeover time + startup "
                "scrap cost) x estimated reduction from optimized sequencing."
            ),
        },
        "increased_throughput": {
            "description": "Better constraint utilization increases output without capital investment",
            "how_to_quantify": (
                "Additional throughput units per day x contribution margin per unit. "
                "Even a 5% throughput improvement on a $50M revenue line is $2.5M."
            ),
        },
        "reduced_expediting_labor": {
            "description": "Fewer fire drills means planners plan instead of expedite",
            "how_to_quantify": (
                "Hours per week spent expediting x loaded labor cost x 52 weeks. "
                "If 2 FTEs spend 50% of their time expediting, that's $100K+ in "
                "labor misallocation."
            ),
        },
    },
    "typical_payback": (
        "APS implementations typically pay for themselves within 6-12 months through "
        "combined savings in overtime, premium freight, inventory, and throughput gains. "
        "Total first-year savings of $500K-$2M are common for mid-size plants "
        "($50-200M revenue)."
    ),
}


# ===========================================================================
# PUBLIC API — single function to retrieve all domain knowledge
# ===========================================================================


def get_domain_knowledge() -> Dict[str, Any]:
    """
    Return the complete APS domain knowledge corpus as a single dictionary.

    Keys:
        scheduling_concepts: Production scheduling theory and methods
        industry_pain_points: Pain points by manufacturing vertical
        integration_patterns: How APS connects to ERP/MES/OEE/SCADA
        key_metrics: OTD, OEE, throughput, WIP, etc.
        common_objections: Sales objections and evidence-based rebuttals
        maturity_model: Scheduling maturity levels (0-5)
        operational_language: Real vocabulary by role and context
        vendor_landscape: APS market overview (vendor-agnostic)
        roi_framework: How to build the business case
    """
    return {
        "scheduling_concepts": SCHEDULING_CONCEPTS,
        "industry_pain_points": INDUSTRY_PAIN_POINTS,
        "integration_patterns": INTEGRATION_PATTERNS,
        "key_metrics": KEY_METRICS,
        "common_objections": COMMON_OBJECTIONS,
        "maturity_model": MATURITY_MODEL,
        "operational_language": OPERATIONAL_LANGUAGE,
        "vendor_landscape": APS_VENDOR_LANDSCAPE,
        "roi_framework": ROI_FRAMEWORK,
    }


def get_industry_knowledge(industry_key: str) -> Dict[str, Any]:
    """
    Retrieve pain points and scheduling context for a specific industry.

    Valid keys: aerospace, automotive, food_and_beverage,
    pharma_life_sciences, medical_device, metals, cpg, plastics
    """
    if industry_key not in INDUSTRY_PAIN_POINTS:
        available = ", ".join(sorted(INDUSTRY_PAIN_POINTS.keys()))
        raise KeyError(f"Unknown industry key '{industry_key}'. Available: {available}")
    return INDUSTRY_PAIN_POINTS[industry_key]


def get_objection_response(objection_substring: str) -> Optional[Dict[str, Any]]:
    """
    Find the best-matching objection response by substring match.

    Example: get_objection_response("Excel") returns the "planners use Excel" objection.
    """
    needle = objection_substring.lower()
    for obj in COMMON_OBJECTIONS:
        if needle in obj["objection"].lower():
            return obj
    return None


def get_maturity_level(level: int) -> Optional[Dict[str, Any]]:
    """Return details for a specific maturity level (0-5)."""
    for lvl in MATURITY_MODEL["levels"]:
        if lvl["level"] == level:
            return lvl
    return None


def get_role_language(role_key: str) -> Dict[str, Any]:
    """
    Retrieve operational language data for a specific role.

    Valid keys: plant_scheduler_planner, production_supervisor_shift_lead,
    vp_operations_coo, supply_chain_director, it_ot_stakeholder
    """
    roles = OPERATIONAL_LANGUAGE["by_role"]
    if role_key not in roles:
        available = ", ".join(sorted(roles.keys()))
        raise KeyError(f"Unknown role key '{role_key}'. Available: {available}")
    return roles[role_key]
