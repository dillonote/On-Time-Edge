"""
Supply chain planning and execution domain knowledge module.

Expert-level reference for On Time Edge implementation consultants.
Covers the full spectrum from strategic planning through shop-floor
execution, vendor landscape, failure modes, and manufacturing
methodologies.

Structured as importable Python data so it can be consumed by
other modules, used in LLM prompts, or serialized to JSON/YAML.

Usage:
    from supply_chain_knowledge import DOMAIN_KNOWLEDGE
    # Access any section:
    hierarchy = DOMAIN_KNOWLEDGE["planning_hierarchy"]
    sop = DOMAIN_KNOWLEDGE["sop_ibp"]
    mrp = DOMAIN_KNOWLEDGE["mrp_mps"]
    execution = DOMAIN_KNOWLEDGE["execution"]
    digital = DOMAIN_KNOWLEDGE["digital_transformation"]
    failures = DOMAIN_KNOWLEDGE["aps_failure_modes"]
    vendors = DOMAIN_KNOWLEDGE["vendor_landscape"]
    methodologies = DOMAIN_KNOWLEDGE["manufacturing_methodologies"]
"""

from typing import Any, Dict, List

# ============================================================================
# 1. SUPPLY CHAIN PLANNING HIERARCHY
# ============================================================================

PLANNING_HIERARCHY: Dict[str, Any] = {
    "overview": (
        "Supply chain planning operates as a cascading hierarchy where each "
        "level sets the constraints and objectives for the level below it. "
        "Decisions made at higher levels are longer-horizon, less granular, "
        "and less frequently revised. Lower levels are shorter-horizon, more "
        "granular, and revised more frequently. The critical challenge is "
        "maintaining coherence across levels so that execution-level decisions "
        "remain aligned with strategic intent."
    ),
    "levels": {
        "strategic": {
            "name": "Strategic Planning / Network Design",
            "horizon": "2-10 years",
            "revision_frequency": "Annual or event-driven",
            "granularity": "Product families, regions, facility-level",
            "key_decisions": [
                "Number, location, and capacity of manufacturing facilities",
                "Make-vs-buy decisions for product families",
                "Supplier base structure and sourcing strategy",
                "Distribution network topology (DCs, hubs, 3PLs)",
                "Capital investment in equipment and automation",
                "Product portfolio decisions and market entry/exit",
                "Long-term capacity acquisition (equipment, labor, buildings)",
                "Global trade and tariff optimization",
            ],
            "tools_and_methods": [
                "Mixed-integer linear programming (MILP) for network optimization",
                "Scenario modeling and Monte Carlo simulation",
                "Geographic information systems (GIS) for facility placement",
                "Total cost of ownership (TCO) models",
                "Tools: Coupa / LLamasoft, AIMMS, Llamasoft (now Coupa), anyLogistix",
            ],
            "feeds_to_next_level": (
                "Strategic decisions set the physical network, capacity envelope, "
                "and sourcing structure within which tactical planning operates. "
                "A tactical plan cannot schedule production at a facility that "
                "does not exist or source from a supplier not yet qualified."
            ),
            "ote_relevance": (
                "OTE consultants encounter strategic decisions when clients are "
                "evaluating new facility scheduling rollouts, global template "
                "deployments, or post-M&A system consolidation. The MDIF framework "
                "addresses this level through current/future state mapping and "
                "digital master plans."
            ),
        },
        "tactical": {
            "name": "Tactical Planning / S&OP / IBP",
            "horizon": "3-18 months (rolling)",
            "revision_frequency": "Monthly (S&OP cycle) with weekly exception reviews",
            "granularity": "Product families, plant-level capacity, monthly/weekly buckets",
            "key_decisions": [
                "Demand-supply balancing across the planning horizon",
                "Rough-cut capacity allocation by plant and product family",
                "Inventory policy targets (safety stock levels, weeks of supply)",
                "Workforce planning (headcount, shifts, overtime authorization)",
                "Supplier commitment volumes and long-lead-time material orders",
                "New product introduction (NPI) timing and ramp plans",
                "Revenue and margin mix optimization",
                "Interplant transfer policies and allocation rules",
            ],
            "tools_and_methods": [
                "S&OP / IBP platforms (Kinaxis, SAP IBP, o9 Solutions, Blue Yonder)",
                "Rough-cut capacity planning (RCCP)",
                "Consensus forecasting processes",
                "Statistical demand planning with demand sensing overlays",
                "What-if scenario analysis for demand/supply trade-offs",
                "Financial reconciliation and P&L simulation",
            ],
            "feeds_to_next_level": (
                "Tactical plans produce a production plan (aggregate output rates "
                "by plant and product family) and authorized inventory/capacity "
                "policies that constrain the master production schedule. Without "
                "a stable tactical plan, MPS/MRP operates without guardrails and "
                "amplifies demand signal noise into the supply base."
            ),
            "ote_relevance": (
                "Many APS implementations fail because the S&OP process feeding "
                "them is broken. OTE consultants must assess S&OP maturity before "
                "scoping an APS project. If the demand signal into the scheduling "
                "engine is unstable, no amount of scheduling sophistication will "
                "fix the downstream chaos."
            ),
        },
        "operational": {
            "name": "Operational Planning / MPS / MRP",
            "horizon": "1 day to 12 weeks (MPS), real-time to 4 weeks (MRP)",
            "revision_frequency": "Daily to weekly (MPS), daily or real-time (MRP)",
            "granularity": "Individual SKUs, work orders, purchase orders, daily buckets",
            "key_decisions": [
                "Master production schedule: what to make, in what quantity, when",
                "Material requirements: what to buy, how much, when to receive",
                "Planned order release timing and quantities",
                "Rescheduling actions for existing orders (expedite, defer, cancel)",
                "Safety stock consumption and replenishment triggers",
                "Lot sizing decisions (EOQ, period order quantity, lot-for-lot)",
                "Allocation of constrained materials to competing demands",
            ],
            "tools_and_methods": [
                "MRP explosion logic (dependent demand calculation)",
                "MPS time-fence management",
                "Pegging (linking supply to demand for traceability)",
                "Exception-based planning (action/rescheduling messages)",
                "Net change vs. regenerative MRP runs",
                "ERP systems (SAP, Oracle, Infor, Epicor, IQMS/DELMIAworks)",
            ],
            "feeds_to_next_level": (
                "MPS/MRP produces planned and firm planned orders that become the "
                "input to detailed scheduling. The scheduler takes the 'what and when' "
                "from MRP and determines the 'how, where, and in what sequence' at "
                "the resource level. Without clean MRP output, the scheduler is "
                "sequencing garbage."
            ),
            "ote_relevance": (
                "This is the critical handoff zone for APS implementations. Most "
                "APS tools sit between MRP and execution, consuming MRP output and "
                "producing a feasible, optimized sequence. OTE consultants must "
                "deeply understand MRP mechanics to configure the APS correctly, "
                "set appropriate time fences, and handle the MRP-APS synchronization "
                "that is the #1 integration challenge in most deployments."
            ),
        },
        "execution": {
            "name": "Execution / Detailed Scheduling / Shop Floor Control",
            "horizon": "Current shift to 2 weeks",
            "revision_frequency": "Real-time to hourly",
            "granularity": (
                "Individual operations, machine-level, minute/hour resolution"
            ),
            "key_decisions": [
                "Operation sequencing on specific machines/work centers",
                "Setup optimization (minimizing changeover time and frequency)",
                "Split and overlap operations to meet due dates",
                "Alternate routing selection based on current availability",
                "Operator assignment and skill-based scheduling",
                "Batch sizing for process industries (reactor, kiln, oven loads)",
                "Real-time rescheduling in response to disruptions",
                "Priority dispatching when multiple orders compete for a resource",
            ],
            "tools_and_methods": [
                "Finite capacity scheduling (FCS) engines",
                "APS tools: Kinaxis Maestro, Siemens Opcenter APS, DELMIA Ortems, "
                "PlanetTogether, Optessa",
                "Gantt chart visualization and drag-drop rescheduling",
                "Dispatching rules: EDD, SPT, critical ratio, bottleneck-first",
                "Constraint-based scheduling (Theory of Constraints DBR)",
                "MES integration for real-time progress feedback",
                "Digital twin simulation for what-if scenarios",
            ],
            "feeds_to_next_level": (
                "Execution results feed back upward: actual production completions "
                "update MRP on-hand and WIP; actual cycle times update planning "
                "parameters; actual demand consumption updates the S&OP forecast. "
                "This closed-loop feedback is essential for plan accuracy and is "
                "exactly where most organizations are weakest."
            ),
            "ote_relevance": (
                "This is OTE's core competency. Detailed scheduling implementation "
                "is where the 30+ years of expertise and 1000+ site deployments "
                "concentrate. The challenge is not just configuring the tool but "
                "modeling the right constraints, integrating with MES for real-time "
                "feedback, and getting planners/schedulers to trust and use the system."
            ),
        },
    },
    "cross_level_challenges": [
        {
            "challenge": "Horizon alignment",
            "description": (
                "Each level operates on a different time horizon. When these horizons "
                "overlap (e.g., the near-term end of the S&OP plan overlaps with "
                "the far end of MPS), conflicts arise about which plan governs. "
                "Time fences are the primary mechanism for managing this overlap."
            ),
        },
        {
            "challenge": "Granularity mismatch",
            "description": (
                "Strategic and tactical plans deal in product families and monthly "
                "buckets. Operational and execution plans deal in SKUs and hours. "
                "Disaggregation (breaking families into SKUs) and aggregation "
                "(rolling SKUs into families) introduce error at every translation."
            ),
        },
        {
            "challenge": "Frequency synchronization",
            "description": (
                "S&OP runs monthly, MRP runs daily, and the scheduler runs "
                "continuously. If the S&OP assumptions change but are not "
                "communicated until the next monthly cycle, MRP and scheduling "
                "operate on stale assumptions for weeks."
            ),
        },
        {
            "challenge": "System integration",
            "description": (
                "Each level often lives in a different system (IBP platform, ERP, "
                "APS, MES). Data must flow bidirectionally across these systems "
                "with appropriate latency, transformation, and conflict resolution. "
                "This is the ISA-95 integration layer that OTE specializes in."
            ),
        },
    ],
}


# ============================================================================
# 2. S&OP / IBP PROCESS
# ============================================================================

SOP_IBP: Dict[str, Any] = {
    "overview": (
        "Sales and Operations Planning (S&OP) is a monthly cross-functional "
        "process that balances demand, supply, and financial plans into a "
        "single integrated operating plan. Integrated Business Planning (IBP) "
        "extends S&OP by adding financial integration, portfolio management, "
        "and strategic alignment. The goal is to give leadership a single "
        "set of numbers to run the business, replacing functional silos where "
        "sales has one forecast, operations has another, and finance has a third."
    ),
    "standard_sop_cycle": {
        "description": "The classic 5-step monthly S&OP cycle",
        "steps": [
            {
                "step": 1,
                "name": "Data Gathering / Product Review",
                "timing": "Week 1",
                "activities": [
                    "Collect actual sales, shipments, inventory data from prior month",
                    "Review new product introduction (NPI) status and timelines",
                    "Assess product lifecycle stage (launch, growth, mature, decline, EOL)",
                    "Update product portfolio assumptions",
                    "Identify product-level risks and opportunities",
                ],
                "owner": "Product Management / Marketing",
                "output": "Updated product assumptions and NPI calendar",
            },
            {
                "step": 2,
                "name": "Demand Review",
                "timing": "Week 2",
                "activities": [
                    "Generate statistical baseline forecast (time series models)",
                    "Overlay demand sensing signals (POS data, channel inventory, web traffic)",
                    "Conduct consensus forecasting: sales overlays market intelligence",
                    "Review forecast accuracy metrics (MAPE, bias, tracking signal)",
                    "Document demand risks (upside and downside scenarios)",
                    "Finalize unconstrained demand plan",
                ],
                "owner": "Demand Planning / Sales",
                "output": "Consensus demand plan (unconstrained) with risk scenarios",
            },
            {
                "step": 3,
                "name": "Supply Review",
                "timing": "Week 3",
                "activities": [
                    "Run rough-cut capacity planning (RCCP) against demand plan",
                    "Identify capacity gaps and material constraints",
                    "Evaluate supply alternatives (overtime, outsourcing, alternate sources)",
                    "Assess supplier risk and lead time changes",
                    "Develop constrained supply plan with options",
                    "Calculate inventory projections and service level impacts",
                ],
                "owner": "Supply Planning / Operations",
                "output": "Constrained supply plan with gap analysis and options",
            },
            {
                "step": 4,
                "name": "Financial Reconciliation / Pre-S&OP",
                "timing": "Week 3-4",
                "activities": [
                    "Translate operational plans into financial impact (revenue, margin, inventory $)",
                    "Compare operating plan to annual operating plan (AOP) / budget",
                    "Quantify cost of supply alternatives (overtime premium, expedite freight)",
                    "Identify trade-offs requiring executive decision",
                    "Prepare decision packages with options and financial consequences",
                ],
                "owner": "Finance / FP&A",
                "output": "Financial view of demand-supply scenarios with decision recommendations",
            },
            {
                "step": 5,
                "name": "Executive S&OP Meeting",
                "timing": "Week 4",
                "activities": [
                    "Review KPIs: forecast accuracy, on-time delivery, inventory turns, margin",
                    "Make decisions on demand-supply gaps (which scenarios to authorize)",
                    "Approve resource commitments (overtime, capital, headcount changes)",
                    "Align on one operating plan across all functions",
                    "Assign action items with owners and deadlines",
                    "Communicate decisions downward to MPS/MRP planners",
                ],
                "owner": "GM / VP Operations / Executive Leadership",
                "output": "Authorized operating plan — the single set of numbers",
            },
        ],
    },
    "ibp_extensions_beyond_sop": [
        {
            "extension": "Financial integration",
            "description": (
                "IBP links the volume plan directly to P&L, balance sheet, and "
                "cash flow projections. Every demand-supply decision has a visible "
                "financial consequence. This replaces the common S&OP failure where "
                "operations has a plan in units and finance has a plan in dollars "
                "and nobody reconciles them until quarter-end."
            ),
        },
        {
            "extension": "Portfolio and product management",
            "description": (
                "IBP incorporates new product lifecycle management, cannibalizations, "
                "and portfolio mix decisions into the planning process rather than "
                "treating them as exogenous inputs."
            ),
        },
        {
            "extension": "Strategic alignment",
            "description": (
                "IBP connects the 18-month rolling plan to the 3-5 year strategic "
                "plan, ensuring that monthly decisions remain consistent with "
                "long-term strategic direction. Gaps between the operating plan and "
                "strategic targets trigger escalation."
            ),
        },
        {
            "extension": "Multi-enterprise visibility",
            "description": (
                "Mature IBP processes extend beyond the four walls to include key "
                "supplier capacity and customer demand signals, creating a more "
                "realistic constraint picture."
            ),
        },
    ],
    "demand_planning_concepts": {
        "demand_sensing_vs_demand_planning": {
            "demand_planning": {
                "definition": (
                    "Mid-to-long-term demand forecasting using statistical models "
                    "(exponential smoothing, ARIMA, Croston's for intermittent demand) "
                    "combined with human judgment overlays from sales and marketing."
                ),
                "horizon": "3-18 months",
                "granularity": "Product family or SKU by month",
                "data_sources": [
                    "Historical shipment/sales data",
                    "Sales pipeline and opportunity data",
                    "Marketing promotions calendar",
                    "Economic indicators and market indices",
                    "Customer forecasts and contracts",
                ],
                "weakness": (
                    "Inherently lagging. Statistical models extrapolate the past. "
                    "Human overlays are biased (sandbagging, optimism). The further "
                    "out the horizon, the wider the error band."
                ),
            },
            "demand_sensing": {
                "definition": (
                    "Short-term demand signal correction using real-time or near-real-time "
                    "downstream data to detect demand pattern changes that statistical "
                    "models have not yet captured."
                ),
                "horizon": "0-12 weeks",
                "granularity": "SKU-location by day or week",
                "data_sources": [
                    "Point-of-sale (POS) data",
                    "Channel inventory levels",
                    "Web traffic and search trends",
                    "Weather data (for weather-sensitive products)",
                    "Social media sentiment",
                    "Order backlog and booking velocity",
                ],
                "value_proposition": (
                    "Reduces near-term forecast error by 20-40% by detecting demand "
                    "shifts weeks before they show up in shipment data. Particularly "
                    "valuable for promotional lifts, weather-driven demand, and "
                    "new product launches."
                ),
            },
        },
        "consensus_forecasting": {
            "definition": (
                "A structured process where multiple functional perspectives "
                "(statistical baseline, sales intelligence, marketing plans, "
                "customer commitments) are combined into a single agreed-upon "
                "forecast through a facilitated meeting with documented assumptions."
            ),
            "why_it_matters": (
                "Without consensus, each function operates on its own forecast. "
                "Sales overforecasts to ensure supply availability. Operations "
                "underforecasts to look efficient. Finance uses the budget number "
                "regardless of either. The result: excess inventory of the wrong "
                "products and shortages of the right ones."
            ),
            "best_practices": [
                "Statistical baseline first — human overlays adjust, not replace",
                "Document every override with owner, reason, and magnitude",
                "Track forecast value add (FVA) to measure if human overrides improve or degrade accuracy",
                "Use assumption-based forecasting: 'If promotion X runs in week Y, demand increases Z%'",
                "Measure and publish individual forecaster accuracy to create accountability",
                "Separate the demand forecast from the supply plan — do not let supply constraints corrupt the demand signal",
            ],
        },
        "rough_cut_capacity_planning": {
            "acronym": "RCCP",
            "definition": (
                "A high-level capacity validation technique that checks whether "
                "the demand plan or master production schedule is feasible given "
                "known capacity constraints, without performing a full MRP explosion. "
                "Uses aggregate resource profiles (hours per unit at critical resources) "
                "to estimate capacity requirements."
            ),
            "methods": [
                {
                    "name": "Capacity planning using overall factors (CPOF)",
                    "description": (
                        "Simplest method. Uses total planned production hours and "
                        "historical percentages to allocate load across work centers."
                    ),
                    "accuracy": "Low — suitable for very early feasibility checks",
                },
                {
                    "name": "Bill of labor (BOL) / resource profile approach",
                    "description": (
                        "Uses a resource profile for each product family showing "
                        "hours required at each critical work center per unit. "
                        "Multiplied by planned quantities to estimate load by "
                        "work center by time period."
                    ),
                    "accuracy": "Medium — the standard RCCP method in most ERP systems",
                },
                {
                    "name": "Capacity requirements planning (CRP)",
                    "description": (
                        "Full MRP-driven capacity calculation using actual routings. "
                        "Technically not RCCP (it is detailed) but often grouped here. "
                        "Requires MRP explosion to have run first."
                    ),
                    "accuracy": "High — but computationally expensive and requires detailed data",
                },
            ],
            "role_in_sop": (
                "RCCP is the supply review's primary tool. It answers: 'Can we "
                "make what the demand plan asks for?' If the answer is no, the "
                "supply review identifies options (overtime, outsourcing, demand "
                "shaping) and presents them to the executive S&OP meeting."
            ),
        },
    },
    "why_sop_fails": [
        {
            "failure_mode": "No executive sponsorship or attendance",
            "description": (
                "S&OP without an empowered executive in the room is a reporting "
                "meeting, not a decision meeting. Decisions get deferred, and "
                "functions revert to local optimization."
            ),
            "frequency": "Very common",
        },
        {
            "failure_mode": "Demand and supply not truly reconciled",
            "description": (
                "Each function presents its view but nobody forces alignment. The "
                "meeting ends with two or three plans still in play. The demand "
                "plan says 1000 units, the supply plan assumes 800, and finance "
                "budgeted 900."
            ),
            "frequency": "Common",
        },
        {
            "failure_mode": "Stale or garbage demand signal",
            "description": (
                "If the demand forecast is never updated, never measured, and "
                "nobody is accountable for accuracy, the entire S&OP process is "
                "built on fiction. Garbage in, garbage out propagates all the way "
                "to the shop floor schedule."
            ),
            "frequency": "Common",
        },
        {
            "failure_mode": "Too granular too soon",
            "description": (
                "Attempting to run S&OP at the SKU level instead of product "
                "family level. The meeting bogs down in item-level exceptions "
                "instead of making strategic trade-off decisions."
            ),
            "frequency": "Common in smaller organizations",
        },
        {
            "failure_mode": "No link to financial plan",
            "description": (
                "S&OP produces a volume plan but nobody translates it to revenue, "
                "margin, and cash. Finance ignores it and runs the business off "
                "the budget. Operations is left wondering why approved plans get "
                "overridden by cost-cutting targets."
            ),
            "frequency": "Very common",
        },
        {
            "failure_mode": "Disconnected from scheduling and execution",
            "description": (
                "The S&OP plan exists in a spreadsheet or IBP tool, but nobody "
                "translates it into MPS parameters, production rates, or scheduling "
                "constraints. The scheduler never sees the S&OP output and builds "
                "the schedule from order backlog alone."
            ),
            "frequency": "Extremely common — and the gap OTE often fills",
        },
        {
            "failure_mode": "Insufficient process discipline",
            "description": (
                "Meetings are skipped, action items are not tracked, and the "
                "process degrades into an ad hoc monthly review that adds overhead "
                "without value."
            ),
            "frequency": "Common, especially after the first year",
        },
    ],
    "sop_to_scheduling_connection": (
        "The S&OP process produces an authorized production plan that sets "
        "the boundaries for master scheduling and detailed scheduling. "
        "Specifically:\n"
        "1. The demand plan provides the demand signal that drives MRP.\n"
        "2. RCCP identifies the bottleneck resources the scheduler must manage.\n"
        "3. Inventory targets set the safety stock levels that buffer scheduling.\n"
        "4. Authorized capacity (shifts, overtime) defines the available hours.\n"
        "5. Material commitments determine what the schedule can actually consume.\n\n"
        "When this connection is broken — when the scheduler has no visibility "
        "into S&OP decisions — they are forced to build the schedule from the "
        "bottom up using only the order book, which inevitably conflicts with "
        "the top-down plan. This is the 'Wednesday problem' OTE talks about: "
        "the plan looked good Monday, but by Wednesday the disconnection between "
        "planning and execution has generated enough exceptions to require "
        "a full replan."
    ),
}


# ============================================================================
# 3. MRP / MPS MECHANICS
# ============================================================================

MRP_MPS: Dict[str, Any] = {
    "overview": (
        "Material Requirements Planning (MRP) and Master Production Scheduling "
        "(MPS) are the computational engines of operational planning. MPS "
        "determines what to produce and when at the finished-good or major "
        "subassembly level. MRP explodes the MPS through bills of material to "
        "calculate dependent demand for all components, subassemblies, and raw "
        "materials, then plans the orders needed to satisfy that demand while "
        "respecting lead times, lot sizes, and safety stock."
    ),
    "master_production_schedule": {
        "definition": (
            "The MPS is the disaggregated, time-phased production plan for "
            "individual end items. It is the primary input to MRP and the "
            "primary contract between planning and manufacturing about what "
            "will be produced."
        ),
        "inputs": [
            "Production plan from S&OP (aggregate targets by product family)",
            "Customer orders (firm demand)",
            "Forecast (anticipated demand not yet booked)",
            "Current inventory and scheduled receipts",
            "Safety stock targets",
        ],
        "key_concepts": {
            "planning_horizon": (
                "Must extend at least as far as the cumulative lead time of "
                "the longest product structure. If total lead time from raw "
                "material to finished good is 14 weeks, MPS must be at least "
                "14 weeks to provide visibility for procurement."
            ),
            "time_fences": {
                "definition": (
                    "Points in time that define zones of increasing schedule "
                    "stability. Changes inside a time fence require higher "
                    "authority to approve, protecting execution from unnecessary "
                    "disruption."
                ),
                "types": [
                    {
                        "name": "Demand time fence (DTF)",
                        "description": (
                            "Inside this fence, only actual customer orders drive "
                            "the schedule — forecast is ignored. Prevents forecast "
                            "changes from disrupting near-term production. Typically "
                            "set at 1-4 weeks."
                        ),
                    },
                    {
                        "name": "Planning time fence (PTF) / Firm zone",
                        "description": (
                            "Inside this fence, the system will not automatically "
                            "reschedule orders. Planned orders become firm planned "
                            "orders. Changes require manual planner intervention. "
                            "Typically set at the item's lead time."
                        ),
                    },
                    {
                        "name": "Frozen zone",
                        "description": (
                            "The innermost fence. No changes allowed without "
                            "executive override. Covers orders already released "
                            "to the shop floor or in-process. Typically 1-2 weeks."
                        ),
                    },
                ],
                "purpose": (
                    "Time fences are the primary mechanism for managing MRP "
                    "nervousness. Without them, every demand change propagates "
                    "instantly into rescheduling messages that overwhelm planners "
                    "and destabilize the shop floor."
                ),
            },
            "available_to_promise": (
                "See execution section — ATP is calculated from the MPS to "
                "determine uncommitted supply available for new customer orders."
            ),
        },
    },
    "mrp_explosion": {
        "definition": (
            "The MRP explosion is the core algorithm that walks the bill of "
            "material top-down, calculating gross requirements, netting against "
            "on-hand inventory and scheduled receipts, and generating planned "
            "orders at each BOM level, offset by lead time."
        ),
        "algorithm_steps": [
            {
                "step": 1,
                "name": "Gross requirements calculation",
                "description": (
                    "For each item at each BOM level, determine the total "
                    "quantity needed by time period. At level 0 (finished goods), "
                    "this comes from the MPS. At lower levels, it comes from the "
                    "planned orders of parent items, multiplied by the quantity-per "
                    "in the BOM."
                ),
            },
            {
                "step": 2,
                "name": "Netting",
                "description": (
                    "Subtract on-hand inventory, scheduled receipts (open POs and "
                    "open shop orders), and safety stock requirements from gross "
                    "requirements to calculate net requirements."
                ),
            },
            {
                "step": 3,
                "name": "Lot sizing",
                "description": (
                    "Group net requirements into order quantities using the "
                    "configured lot-sizing rule: lot-for-lot (L4L), economic order "
                    "quantity (EOQ), period order quantity (POQ), fixed order "
                    "quantity (FOQ), or min/max/multiple."
                ),
            },
            {
                "step": 4,
                "name": "Lead time offset",
                "description": (
                    "Offset each planned order receipt backward by the item's "
                    "lead time to determine the planned order release date. For "
                    "manufactured items, this is production lead time. For "
                    "purchased items, this is procurement lead time."
                ),
            },
            {
                "step": 5,
                "name": "BOM explosion (repeat)",
                "description": (
                    "The planned orders from step 4 become the gross requirements "
                    "for the next lower BOM level. Process repeats level by level "
                    "until all raw materials have been planned."
                ),
            },
        ],
        "example": (
            "If MPS requires 100 units of finished good A in week 10, and A's "
            "BOM requires 2 units of component B and 1 unit of component C, "
            "then MRP generates gross requirements of 200 B and 100 C in week 10. "
            "If B has a 2-week lead time, MRP plans a release in week 8. If B "
            "has 50 on hand and 30 scheduled to arrive in week 7, net requirement "
            "is 200 - 50 - 30 = 120 units. If lot size is FOQ of 150, planned "
            "order quantity is 150 with release in week 8."
        ),
    },
    "order_types": {
        "planned_order": {
            "definition": (
                "A system-generated order recommendation that MRP will "
                "automatically move, resize, or delete on the next MRP run. "
                "It is a suggestion, not a commitment."
            ),
            "characteristics": [
                "Automatically created and modified by MRP",
                "No material or capacity committed",
                "Can be moved, resized, or deleted without consequence",
                "Exists only as a planning signal",
            ],
        },
        "firm_planned_order": {
            "definition": (
                "A planned order that has been manually frozen by the planner. "
                "MRP will not automatically change its date or quantity, but it "
                "has not yet been released to execution."
            ),
            "characteristics": [
                "Planner has reviewed and committed to the plan",
                "MRP will not reschedule it (but will flag exceptions)",
                "No material or capacity actually consumed yet",
                "Used inside the planning time fence",
                "Planner uses this to stabilize the near-term plan",
            ],
            "when_to_use": (
                "When the planner has evaluated trade-offs that MRP cannot "
                "see (e.g., a customer priority, a known constraint, a "
                "supplier commitment) and wants to lock the order against "
                "MRP's automated rescheduling."
            ),
        },
        "released_order": {
            "definition": (
                "An order that has been authorized for execution. For "
                "manufactured items, this is a shop order / production order / "
                "work order. For purchased items, this is a purchase order."
            ),
            "characteristics": [
                "Material is allocated or committed",
                "Capacity is reserved (in finite scheduling systems)",
                "Appears on the shop floor dispatch list or PO to supplier",
                "MRP treats it as a scheduled receipt",
            ],
        },
    },
    "pegging": {
        "definition": (
            "Pegging is the ability to trace a supply element (planned order, "
            "firm planned order, or scheduled receipt) back to the specific "
            "demand element(s) it satisfies (customer order, forecast, safety "
            "stock, dependent demand). It answers: 'Why does this order exist?'"
        ),
        "types": [
            {
                "name": "Single-level pegging",
                "description": "Links supply to its immediate parent demand only.",
            },
            {
                "name": "Full pegging / end-to-end pegging",
                "description": (
                    "Traces from a raw material purchase all the way up to the "
                    "customer order that drives it. Essential for customer order "
                    "promising and priority-based scheduling."
                ),
            },
        ],
        "why_it_matters": (
            "Without pegging, a planner cannot determine the impact of a supply "
            "disruption on specific customer orders. If a raw material shipment "
            "is late, pegging tells you which finished goods are affected and "
            "which customers will be impacted. In APS systems, pegging enables "
            "the scheduler to prioritize by customer order urgency rather than "
            "just by due date."
        ),
    },
    "rescheduling_messages": {
        "definition": (
            "Exception messages (also called action messages) generated by MRP "
            "when the current plan does not match the calculated requirement. "
            "They are the primary output a planner works through daily."
        ),
        "common_types": [
            {
                "message": "Reschedule in",
                "meaning": "Order is needed earlier than currently planned — expedite",
            },
            {
                "message": "Reschedule out",
                "meaning": "Order is needed later than currently planned — defer or cancel",
            },
            {
                "message": "Cancel",
                "meaning": "Order is no longer needed — demand has been removed",
            },
            {
                "message": "Release",
                "meaning": "Planned order is due for release based on lead time offset",
            },
            {
                "message": "Expedite",
                "meaning": "Open order will be late relative to need date — take action",
            },
        ],
        "planner_challenge": (
            "In a typical manufacturing environment, MRP generates hundreds to "
            "thousands of rescheduling messages per day. Many are noise: trivial "
            "quantity changes, oscillations caused by lot-sizing interactions, or "
            "reschedule-in/out cycles for the same item. Planners develop 'message "
            "blindness' and stop responding to them, which means legitimate "
            "exceptions are missed. Exception management filters, time fences, and "
            "dampening rules are critical to making MRP output actionable."
        ),
    },
    "nervousness_problem": {
        "definition": (
            "MRP nervousness refers to the instability of MRP outputs when small "
            "changes in demand, supply, or parameters cause large swings in "
            "planned orders. A 5-unit change in demand can cascade through lot "
            "sizing, safety stock, and lead time offset to create reschedule "
            "messages across dozens of components."
        ),
        "causes": [
            "Lot-sizing rules that amplify small demand changes (EOQ rounding)",
            "Safety stock level changes triggering reorder point shifts",
            "Rolling horizon updates introducing new demand at the far end",
            "Forecast revisions that ripple through BOM explosion",
            "Low-level coding changes from BOM edits",
            "Scrap and yield factors creating fractional quantity variations",
        ],
        "mitigation_strategies": [
            {
                "strategy": "Time fences",
                "description": "Prevent automatic rescheduling inside the frozen/firm zones",
            },
            {
                "strategy": "Firm planned orders",
                "description": "Lock near-term plan against automated changes",
            },
            {
                "strategy": "Dampening (rescheduling tolerance)",
                "description": (
                    "Suppress reschedule messages when the date or quantity change "
                    "is below a configured threshold (e.g., ignore reschedule-in "
                    "messages less than 2 days)"
                ),
            },
            {
                "strategy": "Lot-for-lot sizing in near-term",
                "description": "Reduces amplification from lot-size rounding in the short horizon",
            },
            {
                "strategy": "Frozen forecast in near-term",
                "description": "Do not update forecast inside the demand time fence",
            },
            {
                "strategy": "Net change MRP",
                "description": (
                    "Only replan items affected by changes rather than full "
                    "regeneration, reducing the blast radius of each change"
                ),
            },
        ],
    },
    "safety_stock_vs_safety_time": {
        "safety_stock": {
            "definition": (
                "Extra inventory carried as a buffer against demand variability "
                "and supply variability. MRP plans to keep inventory above the "
                "safety stock level by treating it as a permanent demand offset."
            ),
            "when_to_use": [
                "Demand variability is the primary uncertainty (variable order quantities)",
                "Supply is relatively reliable (consistent lead times)",
                "Item is a standard SKU with relatively predictable demand patterns",
                "Multiple customers share the same inventory pool",
            ],
            "calculation_methods": [
                "Fixed quantity (simple but naive)",
                "Statistical: SS = Z * sigma_demand * sqrt(lead_time) for demand uncertainty",
                "Combined: accounts for both demand and supply variability",
                "Service-level-based: target fill rate or cycle service level drives Z factor",
            ],
            "risk": (
                "Excess safety stock ties up working capital and masks underlying "
                "problems (long lead times, unreliable suppliers, inaccurate "
                "forecasts). Should be treated as a symptom to manage, not a "
                "permanent solution."
            ),
        },
        "safety_time": {
            "definition": (
                "A planning buffer that inflates the lead time used by MRP, "
                "causing orders to be planned for receipt earlier than actually "
                "needed. Unlike safety stock, it does not carry visible on-hand "
                "inventory — it creates a time buffer."
            ),
            "when_to_use": [
                "Supply lead time variability is the primary uncertainty",
                "Supplier on-time delivery is unpredictable",
                "Item is custom/configure-to-order with variable production time",
                "You want to buffer execution uncertainty, not demand uncertainty",
            ],
            "risk": (
                "Safety time is invisible in inventory reports — it appears as "
                "orders arriving 'early' rather than as carried stock. This can "
                "create WIP build-up on the shop floor and obscure the true "
                "amount of buffer in the system."
            ),
        },
        "guidance": (
            "Use safety stock for demand uncertainty. Use safety time for supply "
            "uncertainty. In practice, most environments have both, and the "
            "appropriate strategy depends on which source of variability dominates. "
            "APS implementations often reveal that organizations are carrying "
            "safety stock as a substitute for schedule reliability — if the "
            "schedule were feasible and executable, less buffer would be needed."
        ),
    },
    "mrp_vs_aps_relationship": (
        "MRP and APS are complementary, not competing. MRP calculates material "
        "requirements (what to make/buy and when) assuming infinite capacity. "
        "APS takes the MRP output and creates a finite-capacity schedule (the "
        "specific sequence on specific resources). The typical integration pattern "
        "is:\n"
        "1. MRP runs in the ERP and generates planned/firm planned orders.\n"
        "2. These orders are exported to the APS as the scheduling demand.\n"
        "3. APS sequences the orders against finite capacity, resolving conflicts.\n"
        "4. The APS schedule is published back to ERP (as updated order dates) "
        "and to MES (as the dispatch sequence).\n"
        "5. Actuals from MES flow back to ERP, updating MRP's on-hand and WIP.\n\n"
        "The challenge: if MRP and APS are not tightly synchronized, they will "
        "fight each other. MRP rescheduling may conflict with APS-optimized "
        "sequences. This synchronization is one of the most critical and "
        "under-appreciated aspects of an APS implementation."
    ),
}


# ============================================================================
# 4. SUPPLY CHAIN EXECUTION
# ============================================================================

EXECUTION: Dict[str, Any] = {
    "overview": (
        "Supply chain execution translates plans into physical reality: "
        "warehousing, transportation, and order fulfillment. The critical "
        "interface between planning and execution is order promising — "
        "the ability to commit a reliable delivery date to a customer based "
        "on actual supply availability and production capacity."
    ),
    "warehouse_management": {
        "definition": (
            "Warehouse Management Systems (WMS) control and optimize the "
            "movement and storage of materials within a warehouse. They manage "
            "receiving, put-away, inventory tracking, picking, packing, and "
            "shipping."
        ),
        "key_functions": [
            {
                "function": "Receiving and put-away",
                "description": (
                    "Directing inbound materials to optimal storage locations "
                    "based on velocity, size, product characteristics, and "
                    "upcoming demand. Slotting optimization can improve pick "
                    "efficiency by 15-25%."
                ),
            },
            {
                "function": "Inventory management",
                "description": (
                    "Real-time inventory tracking by location, lot, serial "
                    "number, and status (available, quarantine, allocated, "
                    "in-transit). Supports cycle counting and directed "
                    "replenishment from bulk to pick locations."
                ),
            },
            {
                "function": "Order picking",
                "description": (
                    "Wave planning, batch picking, zone picking, and pick-to-light "
                    "or voice-directed picking. Picking strategy selection depends "
                    "on order profile (many orders with few lines vs. few orders "
                    "with many lines)."
                ),
            },
            {
                "function": "Packing and shipping",
                "description": (
                    "Cartonization (optimal box selection), labeling, shipping "
                    "document generation, carrier selection, and load planning. "
                    "Integration with TMS for carrier rate shopping and tracking."
                ),
            },
        ],
        "scheduling_intersection": (
            "WMS feeds scheduling by providing real-time material availability — "
            "the scheduler needs to know not just that material is on hand, but "
            "that it is available (not allocated, not in quarantine, and in a "
            "reachable location). WMS also consumes the schedule to anticipate "
            "staging requirements: what materials need to be kitted and delivered "
            "to the line, and when."
        ),
    },
    "transportation_management": {
        "definition": (
            "Transportation Management Systems (TMS) optimize freight planning "
            "and execution: carrier selection, route optimization, load "
            "consolidation, shipment tracking, and freight audit."
        ),
        "key_functions": [
            "Route optimization and load consolidation",
            "Carrier rate management and rate shopping",
            "Shipment tendering and carrier acceptance",
            "Real-time shipment visibility and tracking",
            "Freight audit and payment",
            "Dock scheduling and yard management",
        ],
        "scheduling_intersection": (
            "Transportation constraints directly affect scheduling. If an order "
            "must ship on Wednesday's truck to make the customer's Friday delivery "
            "window, that constraint flows backward into the production schedule. "
            "Mature operations synchronize TMS shipment windows with production "
            "scheduling to ensure that production completion aligns with outbound "
            "transportation."
        ),
    },
    "order_promising": {
        "overview": (
            "Order promising is the process of committing a delivery date to "
            "a customer. The reliability of this promise is a primary driver of "
            "customer satisfaction, on-time delivery metrics, and ultimately "
            "revenue retention. There are three progressively sophisticated "
            "approaches."
        ),
        "atp": {
            "name": "Available-to-Promise (ATP)",
            "definition": (
                "ATP calculates the uncommitted portion of a company's inventory "
                "and planned production. It answers: 'Given what we have and what "
                "we've already promised, can we fill this new order, and when?'"
            ),
            "logic": {
                "description": "Discrete ATP logic (the most common implementation)",
                "algorithm": [
                    "Start with on-hand inventory",
                    "Add scheduled receipts (MPS production, inbound POs)",
                    "Subtract committed customer orders (already promised)",
                    "The remainder in each time bucket is ATP",
                    "A new order consumes ATP from the earliest bucket with sufficient quantity",
                ],
                "example": (
                    "Week 1: On-hand 100, committed 80 -> ATP = 20\n"
                    "Week 2: MPS receipt 200, committed 150 -> ATP = 50\n"
                    "Week 3: MPS receipt 200, committed 100 -> ATP = 100\n"
                    "New order for 60 units: cannot fill from Week 1 (only 20 ATP), "
                    "can fill from Week 2 (50 ATP) + Week 3 (10 from 100 ATP). "
                    "Earliest full delivery = Week 2 if partial is allowed, "
                    "Week 3 if full shipment required."
                ),
            },
            "limitations": [
                "Assumes infinite capacity — does not check if production is actually feasible",
                "Based on MPS which may not reflect current shop floor reality",
                "Does not consider material availability at the component level",
                "Static snapshot — can be stale between MRP runs",
            ],
        },
        "ctp": {
            "name": "Capable-to-Promise (CTP)",
            "definition": (
                "CTP extends ATP by checking whether the required production "
                "can actually be completed given current capacity constraints "
                "and material availability. It temporarily simulates inserting "
                "the new order into the finite-capacity schedule to determine "
                "if and when it can be fulfilled."
            ),
            "logic": {
                "algorithm": [
                    "Receive order inquiry (item, quantity, requested date)",
                    "Check ATP — if sufficient ATP exists, promise from ATP",
                    "If ATP insufficient, trigger a CTP check:",
                    "  a. Check material availability (component-level netting)",
                    "  b. Check finite capacity at bottleneck resources",
                    "  c. Simulate scheduling the order and calculate completion date",
                    "  d. Return the earliest feasible promise date",
                ],
            },
            "advantages": [
                "Accounts for real capacity constraints, not just planned supply",
                "Considers material availability at all BOM levels",
                "Provides more reliable promise dates, improving on-time delivery",
                "Can evaluate trade-offs: 'If we expedite this order, what else slips?'",
            ],
            "challenges": [
                "Computationally expensive — requires finite scheduling simulation",
                "Requires tight integration between order entry, APS, and MRP",
                "Can create latency in order entry if simulation takes too long",
                "Requires accurate capacity and routing data to produce reliable dates",
            ],
            "ote_relevance": (
                "CTP is a high-value capability that APS enables. Many OTE clients "
                "pursue APS specifically to improve order promising reliability. "
                "The implementation challenge is building the integration between "
                "the order management system (ERP) and the APS engine so that CTP "
                "queries can be answered in real time without blocking order entry."
            ),
        },
        "ptp": {
            "name": "Profitable-to-Promise (PTP)",
            "definition": (
                "PTP extends CTP by adding a profitability dimension: not just "
                "'can we make this?' but 'should we make this?' It considers the "
                "margin contribution of the order, the opportunity cost of capacity "
                "consumed, and whether accepting this order might displace a more "
                "profitable one."
            ),
            "use_cases": [
                "Make-to-order environments with constrained capacity",
                "Industries with significant order-to-order margin variation",
                "Situations where accepting a large low-margin order would block higher-margin work",
            ],
        },
    },
    "mes_integration": {
        "definition": (
            "Manufacturing Execution Systems (MES) bridge the gap between "
            "planning/scheduling systems and the physical shop floor. MES "
            "manages work order execution, tracks real-time production progress, "
            "captures quality data, and provides the actual-vs-plan feedback "
            "loop that scheduling systems need."
        ),
        "isa_95_layers": {
            "description": (
                "ISA-95 (IEC 62264) defines the standard integration architecture "
                "between enterprise (ERP) and control (SCADA/PLC) systems. The "
                "layers relevant to scheduling:"
            ),
            "levels": [
                {
                    "level": 4,
                    "name": "Business Planning & Logistics",
                    "systems": "ERP, IBP, S&OP tools",
                    "time_frame": "Months to years",
                },
                {
                    "level": 3,
                    "name": "Manufacturing Operations Management",
                    "systems": "MES, APS, QMS, WMS, maintenance management",
                    "time_frame": "Shifts to days",
                },
                {
                    "level": 2,
                    "name": "Monitoring, Supervisory, and Automated Control",
                    "systems": "SCADA, HMI, DCS",
                    "time_frame": "Seconds to minutes",
                },
                {
                    "level": 1,
                    "name": "Sensing and Manipulation",
                    "systems": "PLCs, sensors, actuators",
                    "time_frame": "Milliseconds to seconds",
                },
                {
                    "level": 0,
                    "name": "Physical Process",
                    "systems": "The actual production equipment and materials",
                    "time_frame": "Continuous",
                },
            ],
        },
        "mes_to_aps_data_flows": [
            {
                "direction": "MES -> APS",
                "data": [
                    "Actual operation start/end times (for schedule progress tracking)",
                    "Work order status and completion percentages",
                    "Machine status (running, down, setup, idle)",
                    "Actual cycle times and throughput rates",
                    "Quality holds and quarantine events",
                    "Scrap and yield actuals",
                    "Labor availability and attendance",
                ],
                "purpose": (
                    "Enables the APS to reschedule based on actual shop floor "
                    "conditions rather than planned assumptions. This is the "
                    "closed-loop feedback that makes scheduling responsive."
                ),
            },
            {
                "direction": "APS -> MES",
                "data": [
                    "Dispatch list (operation sequence by work center)",
                    "Planned start/end times for each operation",
                    "Batch/lot assignments for process industries",
                    "Tooling and fixture requirements by operation",
                    "Setup type and expected setup duration",
                ],
                "purpose": (
                    "Provides the shop floor with a clear, sequenced work plan "
                    "so operators know what to run next without needing to make "
                    "prioritization decisions themselves."
                ),
            },
        ],
        "ote_relevance": (
            "MES integration is one of OTE's core service offerings. The "
            "Toward Zero heritage (Aaron Muhl, ISA-95 voting member for 12+ "
            "years) gives OTE deep expertise in the Level 3/Level 4 integration "
            "layer where APS, MES, and ERP must exchange data reliably. "
            "Partners include Sepasoft, Parsec/TrakSYS, AVEVA, GE Vernova, "
            "and the new Fuuz/MFGx partnership."
        ),
    },
}


# ============================================================================
# 5. DIGITAL TRANSFORMATION IN MANUFACTURING
# ============================================================================

DIGITAL_TRANSFORMATION: Dict[str, Any] = {
    "overview": (
        "Digital transformation in manufacturing is the systematic adoption "
        "of digital technologies to fundamentally improve operational performance. "
        "It is not a technology project — it is an operational strategy enabled "
        "by technology. The most common failure is treating it as an IT initiative "
        "rather than an operations initiative."
    ),
    "it_ot_convergence": {
        "definition": (
            "The integration of Information Technology (IT) systems — ERP, "
            "APS, BI — with Operational Technology (OT) systems — SCADA, PLCs, "
            "DCS, historians — into a unified architecture where data flows "
            "freely between the shop floor and the enterprise."
        ),
        "why_it_matters": (
            "Historically, IT and OT operated as separate domains with different "
            "teams, different networks, different security models, and different "
            "data formats. This separation means that scheduling decisions in the "
            "IT world (ERP/APS) are disconnected from real-time production data "
            "in the OT world (SCADA/MES). IT/OT convergence eliminates this gap, "
            "enabling scheduling systems to consume real-time machine data and "
            "production systems to receive scheduling directives."
        ),
        "challenges": [
            {
                "challenge": "Security concerns",
                "description": (
                    "OT networks control physical equipment. Connecting them to "
                    "IT networks introduces cybersecurity risks (ransomware, "
                    "unauthorized access to control systems). The Purdue Model "
                    "and IEC 62443 provide security architecture frameworks."
                ),
            },
            {
                "challenge": "Protocol heterogeneity",
                "description": (
                    "OT systems speak protocols like OPC-UA, Modbus, EtherNet/IP, "
                    "PROFINET, MQTT. IT systems speak REST, SOAP, SQL. Middleware "
                    "and edge gateways are needed to translate."
                ),
            },
            {
                "challenge": "Organizational silos",
                "description": (
                    "IT reports to the CIO, OT reports to the VP Manufacturing "
                    "or VP Engineering. Different budgets, different priorities, "
                    "different vendors. Convergence requires organizational "
                    "alignment, not just technical integration."
                ),
            },
            {
                "challenge": "Data volume and velocity",
                "description": (
                    "OT systems generate data at millisecond intervals. IT systems "
                    "operate at transaction-level granularity. Bridging these "
                    "requires edge computing, data historians, and intelligent "
                    "filtering to avoid overwhelming enterprise systems."
                ),
            },
        ],
        "ote_relevance": (
            "IT/OT convergence is central to OTE's value proposition post-merger. "
            "The original On Time Edge brought IT-side expertise (APS, ERP integration) "
            "while Toward Zero brought OT-side expertise (SCADA, MES, ISA-95). "
            "The MDIF framework explicitly addresses the interoperability layer "
            "between IT and OT systems."
        ),
    },
    "digital_thread": {
        "definition": (
            "A digital thread is a continuous, connected data flow linking every "
            "phase of a product's lifecycle: design (CAD/PLM) -> process planning "
            "(CAM/routing) -> production (MES/APS) -> quality (QMS) -> service "
            "(field data). It provides full traceability from design intent to "
            "as-built reality."
        ),
        "value_for_scheduling": [
            "Routing and BOM data flows directly from PLM to APS without manual re-entry",
            "Engineering change orders (ECOs) automatically propagate to affected schedules",
            "As-built records link scheduled operations to actual quality outcomes",
            "Design-for-manufacturability feedback: scheduling data reveals which designs "
            "are hardest to schedule (long setups, constrained resources)",
        ],
        "maturity_reality": (
            "Full digital thread is aspirational for most manufacturers. In practice, "
            "most organizations have significant gaps between PLM and ERP/MES, "
            "requiring manual data translation. APS implementations often surface "
            "these gaps because the scheduler needs accurate routings and BOMs "
            "that the current systems may not provide."
        ),
    },
    "digital_twin_for_scheduling": {
        "definition": (
            "A digital twin for scheduling is a virtual replica of the production "
            "environment — resources, constraints, WIP, material availability — "
            "that can be used to simulate scheduling scenarios without affecting "
            "the live production plan."
        ),
        "use_cases": [
            {
                "use_case": "What-if analysis",
                "description": (
                    "Simulate the impact of accepting a rush order, losing a "
                    "machine, changing shift patterns, or introducing a new product. "
                    "Compare multiple scenarios side by side before committing to "
                    "a schedule change."
                ),
            },
            {
                "use_case": "Training and onboarding",
                "description": (
                    "New schedulers can practice with the digital twin without "
                    "risk to the live schedule. Reduces the 6-12 month learning "
                    "curve for new scheduling staff."
                ),
            },
            {
                "use_case": "Continuous improvement",
                "description": (
                    "Test proposed process improvements (reduced setup times, "
                    "additional resources, new routings) to quantify their "
                    "scheduling impact before investing."
                ),
            },
            {
                "use_case": "S&OP support",
                "description": (
                    "Use the digital twin to validate rough-cut capacity plans "
                    "at a detailed level, providing higher-confidence capacity "
                    "assessments for the S&OP process."
                ),
            },
        ],
        "ote_relevance": (
            "APS tools inherently contain a scheduling model that functions as "
            "a digital twin. OTE's what-if scenario capability in implementations "
            "leverages this. The MDIF framework positions the digital twin as a "
            "key enabler for AI-driven optimization."
        ),
    },
    "iiot_feeding_scheduling": {
        "definition": (
            "The Industrial Internet of Things (IIoT) refers to the network of "
            "sensors, devices, and edge systems that collect real-time data from "
            "the production environment and make it available to enterprise systems."
        ),
        "data_types_relevant_to_scheduling": [
            {
                "data_type": "Machine status and OEE metrics",
                "scheduling_impact": (
                    "Real-time machine availability, performance rate, and quality "
                    "rate. Allows the scheduler to work with actual capacity rather "
                    "than theoretical capacity."
                ),
            },
            {
                "data_type": "Cycle time actuals",
                "scheduling_impact": (
                    "Actual cycle times vs. standard cycle times. If a machine is "
                    "running 15% slower than standard, the schedule should reflect "
                    "that reality rather than the standard."
                ),
            },
            {
                "data_type": "Setup/changeover tracking",
                "scheduling_impact": (
                    "Actual setup durations compared to planned. Feeds setup matrix "
                    "optimization in APS (sequence-dependent setups)."
                ),
            },
            {
                "data_type": "Environmental conditions",
                "scheduling_impact": (
                    "Temperature, humidity, vibration data that affects quality or "
                    "throughput. In some processes (pharma, food), environmental "
                    "conditions constrain what can be produced when."
                ),
            },
            {
                "data_type": "Tool wear and consumable levels",
                "scheduling_impact": (
                    "Remaining tool life affects scheduling: if a tool will need "
                    "replacement mid-batch, the scheduler should account for the "
                    "interruption or schedule the changeover at a natural break point."
                ),
            },
            {
                "data_type": "Energy consumption patterns",
                "scheduling_impact": (
                    "Energy-intensive operations can be scheduled during off-peak "
                    "periods. Real-time energy pricing feeds can drive dynamic "
                    "scheduling optimization."
                ),
            },
        ],
        "integration_architecture": (
            "IIoT data typically flows: Sensor -> Edge Gateway -> Historian/MQTT "
            "Broker -> MES/OEE Platform -> APS. The key architectural decisions "
            "are: (1) what data to collect, (2) what to process at the edge vs. "
            "in the cloud, (3) at what frequency the APS needs updates, and "
            "(4) how to handle data quality issues (missing readings, sensor drift, "
            "calibration errors)."
        ),
    },
    "predictive_maintenance_impact_on_scheduling": {
        "definition": (
            "Predictive maintenance (PdM) uses sensor data, machine learning, "
            "and equipment models to predict when a machine will require "
            "maintenance, enabling maintenance to be scheduled proactively "
            "rather than reactively."
        ),
        "scheduling_intersection": {
            "without_pdm": (
                "Schedulers either: (a) schedule around fixed PM windows (calendar-based "
                "maintenance) which may be too frequent, wasting capacity, or too "
                "infrequent, risking breakdowns; or (b) react to unplanned breakdowns "
                "by emergency rescheduling, which is the #1 source of schedule disruption."
            ),
            "with_pdm": (
                "PdM provides the scheduler with a probability-weighted maintenance "
                "need: 'Machine X has a 70% chance of requiring bearing replacement "
                "within the next 5 days.' The scheduler can then find the optimal "
                "time to schedule maintenance — a natural gap between orders, a "
                "low-demand period, or a time when alternate equipment is available."
            ),
            "integration_requirements": [
                "PdM system must publish maintenance predictions to the APS",
                "APS must be able to model planned maintenance as a capacity constraint",
                "Maintenance work orders must be visible in the scheduling Gantt",
                "Actual maintenance duration must feed back to improve PdM models",
            ],
        },
    },
    "ai_ml_in_planning": {
        "current_applications": [
            {
                "application": "Demand forecasting enhancement",
                "description": (
                    "ML models (gradient boosting, neural networks, transformers) "
                    "can capture complex demand patterns (promotions, weather, events) "
                    "that traditional statistical methods miss. Particularly effective "
                    "for intermittent demand and new product launches."
                ),
                "maturity": "Production-ready in leading organizations",
            },
            {
                "application": "Demand sensing",
                "description": (
                    "Real-time ML models that process POS, web, and channel data "
                    "to detect demand shifts within days rather than waiting for "
                    "the monthly forecast cycle."
                ),
                "maturity": "Production-ready for CPG and retail-adjacent manufacturers",
            },
            {
                "application": "Intelligent scheduling optimization",
                "description": (
                    "Reinforcement learning and genetic algorithms to optimize "
                    "scheduling objectives (minimize makespan, minimize tardiness, "
                    "minimize setups) beyond what rule-based heuristics achieve. "
                    "Increasingly used for setup sequence optimization."
                ),
                "maturity": "Emerging — available in some APS platforms, not yet mainstream",
            },
            {
                "application": "Anomaly detection in planning parameters",
                "description": (
                    "ML models that detect when planning parameters (lead times, "
                    "cycle times, yields, setup times) have drifted from reality "
                    "and recommend corrections."
                ),
                "maturity": "Emerging",
            },
            {
                "application": "Autonomous planning exception handling",
                "description": (
                    "ML models that learn planner behavior patterns to auto-resolve "
                    "routine MRP exceptions (e.g., auto-firm orders that the planner "
                    "always approves), freeing planners for higher-value decisions."
                ),
                "maturity": "Early research — limited production deployments",
            },
            {
                "application": "Supply risk prediction",
                "description": (
                    "NLP and network analysis models that predict supplier "
                    "disruptions from news, financial data, weather, and shipping "
                    "data, enabling proactive supply plan adjustments."
                ),
                "maturity": "Production-ready in leading supply chain platforms",
            },
        ],
        "cautions": [
            "AI/ML requires clean, sufficient training data — most factories do not have this yet",
            "Black-box optimization is resisted by experienced schedulers who need to understand why",
            "AI-generated schedules still need human validation against constraints the model may not know",
            "Explainability is critical for adoption — schedulers will not trust what they cannot verify",
            "Start with augmenting human decisions (recommendations), not replacing them (autonomous)",
        ],
        "ote_perspective": (
            "OTE positions AI as an enabler within the MDIF framework, not as "
            "a replacement for experienced planners. The approach: get the data "
            "foundation right (IIoT, MES, ERP integration), get the scheduling "
            "model right (APS implementation), then layer AI on top for "
            "optimization — forecasting optimal sequences, dynamically rerouting "
            "around disruptions, simulating what-if scenarios, and adjusting "
            "setpoints in real time. Skipping the foundation to jump to AI is "
            "a recipe for expensive disappointment."
        ),
    },
    "industry_4_0_maturity_model": {
        "levels": [
            {
                "level": 1,
                "name": "Computerization",
                "description": "Basic digital systems exist but operate in isolation (standalone ERP, no MES).",
            },
            {
                "level": 2,
                "name": "Connectivity",
                "description": "Systems are connected via networks. Data can flow between IT and OT but is not yet leveraged.",
            },
            {
                "level": 3,
                "name": "Visibility",
                "description": "Real-time data from the shop floor is captured, structured, and visualized. You know what is happening now.",
            },
            {
                "level": 4,
                "name": "Transparency",
                "description": "Root-cause analysis is possible. You understand why things are happening. Data analytics and contextualization.",
            },
            {
                "level": 5,
                "name": "Predictability",
                "description": "Data-driven models predict future states. Predictive maintenance, demand sensing, capacity forecasting.",
            },
            {
                "level": 6,
                "name": "Adaptability",
                "description": "Systems autonomously adapt to changing conditions. Self-optimizing schedules, autonomous exception handling.",
            },
        ],
        "assessment_note": (
            "Most manufacturing organizations are between levels 2 and 3. APS "
            "implementation typically requires at least level 3 (visibility) to "
            "be effective, because the scheduler needs real-time data to produce "
            "feasible schedules. OTE's MDIF framework helps clients assess their "
            "current maturity and build a roadmap."
        ),
    },
}


# ============================================================================
# 6. COMMON FAILURE MODES IN APS IMPLEMENTATIONS
# ============================================================================

APS_FAILURE_MODES: Dict[str, Any] = {
    "overview": (
        "APS implementations have a historically high failure rate — industry "
        "estimates range from 30-60% failing to deliver expected value. The "
        "failures are rarely about the software itself. They are about data, "
        "process, people, and integration. OTE's 1000+ site implementation "
        "experience provides deep pattern recognition for these failure modes."
    ),
    "failure_modes": [
        {
            "category": "Data Quality",
            "failure": "Inaccurate BOMs and routings",
            "description": (
                "The APS schedule is only as good as the data it consumes. If "
                "bills of material are incomplete (missing components, wrong "
                "quantities-per), routings are outdated (operations removed or "
                "added on the floor but not in the system), or work center "
                "definitions do not match physical reality, the schedule will "
                "be infeasible from day one."
            ),
            "symptoms": [
                "Schedule shows operations on machines that don't exist or aren't used for that product",
                "Material shortages despite MRP showing sufficient supply",
                "Scheduled run times that bear no resemblance to actual cycle times",
                "Phantom operations that operators skip every time",
            ],
            "root_causes": [
                "Engineering changes made on the floor but never updated in ERP",
                "Multiple product variants sharing a generic BOM/routing that fits none of them",
                "Standards set years ago and never validated against current equipment/processes",
                "Acquisition of new equipment without updating routing alternatives",
            ],
            "prevention": [
                "Conduct a routing and BOM audit before APS implementation (not during)",
                "Time studies on bottleneck operations to validate cycle time standards",
                "Establish a data governance process for ongoing BOM/routing maintenance",
                "Start APS on a subset of products with clean data, expand as data improves",
            ],
            "ote_approach": (
                "OTE's 3-day kickoff workshop specifically addresses data readiness. "
                "The 90-day implementation target assumes data cleanup runs in "
                "parallel with configuration, with the first phase focusing on "
                "the highest-volume product families at the bottleneck resources."
            ),
        },
        {
            "category": "Data Quality",
            "failure": "Inaccurate or missing planning parameters",
            "description": (
                "Setup times, run rates, scrap factors, yield rates, batch sizes, "
                "and lead times in ERP rarely match reality. Setup times are "
                "particularly problematic because they are often stored as a "
                "single fixed value when they are actually sequence-dependent "
                "(the setup time depends on what was running before)."
            ),
            "symptoms": [
                "APS schedules consistently too tight or too loose",
                "Planned setup time is 30 minutes but actual is 2 hours",
                "Yield/scrap assumptions cause over- or under-production",
                "Lead times in ERP are inflated 'safety padded' values that the APS treats as real",
            ],
            "prevention": [
                "Build and validate setup matrices for bottleneck resources (sequence-dependent setups)",
                "Replace safety-padded ERP lead times with actual lead times in the APS model",
                "Implement continuous parameter calibration using MES actuals",
                "Start with conservative (longer) parameters and tighten as confidence grows",
            ],
        },
        {
            "category": "Change Management",
            "failure": "Planners and schedulers won't use the system",
            "description": (
                "The most technically perfect APS implementation fails if the "
                "schedulers refuse to use it. Experienced schedulers have built "
                "mental models of their plant over years. They schedule from "
                "memory, relationships, and intuition. An APS that ignores this "
                "knowledge and imposes a 'system knows best' approach will be "
                "abandoned within months."
            ),
            "symptoms": [
                "Schedulers maintain parallel spreadsheets and use APS only for reporting",
                "Schedulers override every APS suggestion without reviewing it",
                "The APS schedule and the actual dispatch sequence are completely different",
                "After go-live, schedulers revert to the old process within 90 days",
            ],
            "root_causes": [
                "Schedulers were not involved in requirements gathering or model design",
                "The APS model does not capture constraints the scheduler knows from experience",
                "Training was focused on buttons and menus, not scheduling concepts and workflow",
                "Schedulers perceive the APS as a threat to their job or expertise",
                "The APS produces infeasible schedules, so schedulers learn to distrust it",
            ],
            "prevention": [
                "Involve the head scheduler as a core team member from day 1",
                "Model constraints iteratively with scheduler validation at each step",
                "Frame the APS as a power tool for the scheduler, not a replacement",
                "Start with a simplified model that produces mostly-right schedules, then refine",
                "Measure adoption metrics (how often the APS schedule matches actual dispatch)",
                "Celebrate wins where the APS helped avoid a problem the scheduler might have missed",
            ],
            "ote_approach": (
                "OTE's Theory of Constraints methodology naturally centers the "
                "scheduler: the binding constraint is identified collaboratively, "
                "and the APS is built around the constraints the scheduler already "
                "manages. The 3-day workshop aligns the workforce behind goals "
                "before any technical work begins."
            ),
        },
        {
            "category": "Change Management",
            "failure": "Lack of organizational readiness",
            "description": (
                "APS implementation is treated as a software project rather than "
                "an operational transformation. No executive sponsor, no defined "
                "KPIs, no process changes to support the new workflow, no dedicated "
                "project team."
            ),
            "symptoms": [
                "Project team members are assigned part-time and can't attend meetings",
                "Nobody can articulate what success looks like in measurable terms",
                "Go-live happens but nobody changes their daily process",
                "The APS becomes shelfware within 6 months",
            ],
            "prevention": [
                "Secure executive sponsorship with clear KPI targets before starting",
                "Define the target operating model: who does what differently after APS",
                "Assign a dedicated project team (at minimum: scheduler, planner, IT, operations)",
                "Plan for a parallel-run period where old and new processes coexist",
                "Build a benefits realization plan that tracks value delivered post-go-live",
            ],
        },
        {
            "category": "Over-Modeling",
            "failure": "Trying to model every constraint on day one",
            "description": (
                "The impulse to build a 'perfect' model that captures every "
                "constraint, every alternate routing, every sequence-dependent "
                "setup, every operator skill, every tool requirement is the "
                "enemy of a successful go-live. Over-modeled systems take too "
                "long to implement, are too fragile to maintain, and produce "
                "results that nobody can understand or debug."
            ),
            "symptoms": [
                "Implementation timeline exceeds 12 months with no go-live in sight",
                "The model has hundreds of constraints but nobody can explain which ones matter",
                "Solver run times are unacceptably long (minutes or hours instead of seconds)",
                "Minor data changes cause catastrophic schedule shifts",
                "Nobody but the original consultant can maintain the model",
            ],
            "root_causes": [
                "Attempting to replicate the scheduler's complete mental model in software",
                "Including non-binding constraints that never actually limit the schedule",
                "Modeling theoretical processes rather than actual current-state processes",
                "Vendor or consultant incentivized by project hours rather than outcomes",
            ],
            "prevention": [
                "Start with the binding constraint and the top 5-10 secondary constraints",
                "Apply the 80/20 rule: model the constraints that affect 80% of scheduling decisions",
                "Validate each constraint addition with: 'Does this change the schedule materially?'",
                "Plan for iterative refinement: Phase 1 (core model), Phase 2 (refinements), Phase 3 (optimization)",
                "Set a time-boxed go-live date and scope the model to what can be done by then",
            ],
            "ote_approach": (
                "OTE's TOC-based approach inherently prevents over-modeling: "
                "you identify the binding constraint, build the schedule around "
                "it, and add complexity only when the constraint shifts. The 90-day "
                "time-to-first-value target forces disciplined scope management."
            ),
        },
        {
            "category": "Integration",
            "failure": "APS disconnected from MES and ERP",
            "description": (
                "The APS operates as an island. Planned orders are manually "
                "exported from ERP, the schedule is manually communicated to the "
                "floor, and actual progress is not fed back to the APS. The "
                "schedule becomes stale within hours of publication."
            ),
            "symptoms": [
                "Schedulers re-enter data from ERP into APS manually (double entry)",
                "The APS schedule is published as a PDF or printout, not a live dispatch",
                "Shop floor status requires walking the floor or calling supervisors",
                "By afternoon, the morning's schedule is fiction",
                "Nobody trusts the APS because it does not reflect current reality",
            ],
            "root_causes": [
                "Integration budget was cut to save on project costs",
                "APS was purchased before MES existed, and nobody planned the connection",
                "ERP and APS vendors have incompatible data models or APIs",
                "No IT resources allocated to build and maintain integration interfaces",
            ],
            "prevention": [
                "Budget for integration as 30-50% of total APS project cost",
                "Define integration requirements (data, frequency, direction) before vendor selection",
                "Use standard integration patterns (ISA-95 B2MML, OPC-UA, REST APIs)",
                "Implement MES or at minimum a shop floor data collection mechanism before or alongside APS",
                "Plan for bidirectional flow: ERP -> APS (demand/supply) and MES -> APS (actuals)",
            ],
            "ote_approach": (
                "Systems integration is a core OTE service offering. The MDIF "
                "framework explicitly addresses integration architecture across "
                "ISA-88/95 layers. OTE's partnerships span ERP, APS, MES, and "
                "OT vendors, enabling end-to-end integration design."
            ),
        },
        {
            "category": "Post-Go-Live",
            "failure": "No post-go-live optimization or support",
            "description": (
                "The implementation team leaves after go-live. The model is "
                "never refined. Planning parameters drift from reality. New "
                "products are added without updating the scheduling model. "
                "Performance degrades gradually until the system is abandoned."
            ),
            "symptoms": [
                "Schedule quality degrades over months as the model drifts from reality",
                "New products are scheduled with default parameters because nobody updates the model",
                "The consultant left and nobody internally knows how to modify the model",
                "The original ROI case is never validated because nobody measures post-go-live",
            ],
            "prevention": [
                "Build internal APS expertise — do not depend solely on external consultants",
                "Establish a model maintenance process: monthly parameter review, quarterly model audit",
                "Contract for post-go-live support (this is OTE's managed services offering)",
                "Track scheduling KPIs continuously: schedule adherence, on-time delivery, setup efficiency",
                "Plan a Phase 2 optimization starting 3-6 months after go-live",
            ],
            "ote_approach": (
                "OTE's managed services (MSP) offering is specifically designed "
                "to address this failure mode. Post-go-live system health, upgrades, "
                "process optimization, and ongoing model refinement. The positioning: "
                "'We don't disappear after go-live.'"
            ),
        },
    ],
    "success_factors": [
        "Executive sponsorship with clear, measurable KPIs",
        "Dedicated scheduler involvement throughout the project",
        "Clean data on the critical path — BOM/routing audit before configuration",
        "Start simple, iterate — 80/20 model, not a perfect model",
        "Tight integration with ERP and MES from day one",
        "Post-go-live support and continuous optimization",
        "Theory of Constraints mindset: focus on the binding constraint",
        "90-day time-to-first-value to maintain momentum and demonstrate ROI",
    ],
}


# ============================================================================
# 7. VENDOR LANDSCAPE CONTEXT
# ============================================================================

VENDOR_LANDSCAPE: Dict[str, Any] = {
    "overview": (
        "The APS vendor landscape is fragmented, with solutions ranging from "
        "niche scheduling tools to broad supply chain planning suites. No single "
        "vendor excels at everything. The right choice depends on the "
        "manufacturer's industry, production type (discrete, process, hybrid), "
        "ERP environment, scheduling complexity, and organizational maturity. "
        "OTE's vendor-agnostic positioning is grounded in the reality that "
        "recommending the wrong tool is worse than recommending no tool at all."
    ),
    "vendors": {
        "kinaxis_maestro": {
            "full_name": "Kinaxis Maestro (formerly RapidResponse)",
            "category": "End-to-end supply chain orchestration platform",
            "architecture": "Cloud-native (SaaS), in-memory concurrent planning",
            "sweet_spot": (
                "Mid-to-large enterprises needing concurrent planning across "
                "demand, supply, S&OP, inventory, and order fulfillment in a "
                "single platform. Strong for multi-site, multi-tier supply "
                "chain visibility."
            ),
            "strengths": [
                "Concurrent planning: demand, supply, capacity, and inventory planned simultaneously, not sequentially",
                "Scenario management: powerful what-if analysis with side-by-side comparison",
                "Supply chain orchestration: goes beyond scheduling to encompass S&OP, demand planning, and order management",
                "In-memory computation: fast recalculation even with large data sets",
                "Strong ecosystem and partner network",
                "Rapid deployment methodology for faster time-to-value",
                "Emerging AI/ML capabilities for demand sensing and autonomous planning",
            ],
            "weaknesses": [
                "Detailed finite scheduling (minute-level, sequence-dependent setups) is not its core strength",
                "Can be complex to configure for highly customized manufacturing environments",
                "Premium pricing — may be over-scoped for single-plant scheduling needs",
                "Best value realized when deploying multiple planning modules, not just scheduling",
            ],
            "best_for": [
                "Multi-site manufacturers needing supply chain-wide planning",
                "Organizations wanting a single platform for S&OP through execution",
                "Companies with complex multi-tier supply networks",
                "Manufacturers needing strong scenario analysis and what-if capabilities",
            ],
            "ote_relationship": (
                "Major strategic partner — OTE is a Kinaxis SI, Solution Extension "
                "partner, and VAR. Brian Lindenmeyer (VP Strategy & Partnerships) "
                "was hired specifically to expand the Kinaxis go-to-market. This is "
                "OTE's deepest vendor relationship."
            ),
        },
        "siemens_opcenter_aps": {
            "full_name": "Siemens Opcenter APS (formerly Preactor)",
            "category": "Dedicated finite capacity scheduling",
            "architecture": "On-premise and cloud options, client-server",
            "sweet_spot": (
                "Discrete and hybrid manufacturers needing detailed shop-floor "
                "scheduling with finite capacity, sequence-dependent setups, "
                "and Gantt-based visual scheduling."
            ),
            "strengths": [
                "Deep finite capacity scheduling: sequence-dependent setups, split operations, overlap, alternate routings",
                "Mature product with decades of refinement (Preactor founded 1992)",
                "Strong Gantt visualization with interactive drag-and-drop rescheduling",
                "Scalable from single-plant to multi-plant deployments",
                "Three tiers: Express (simple), Standard (mid), Professional (advanced) — fits different complexity levels",
                "Sequence-dependent setup optimization is a particular strength",
                "Broad industry coverage: discrete, process, and hybrid",
                "Part of the Siemens Xcelerator portfolio — integrates with Teamcenter (PLM), "
                "Opcenter Execution (MES), and the broader Siemens ecosystem",
            ],
            "weaknesses": [
                "S&OP and demand planning capabilities are limited — focused on scheduling, not planning",
                "UI/UX can feel dated compared to newer cloud-native platforms",
                "Integration with non-Siemens ERP systems requires more effort",
                "Advanced optimization features require Professional tier licensing",
            ],
            "best_for": [
                "Discrete manufacturers with complex job-shop or flow-shop scheduling",
                "Plants with significant sequence-dependent setup challenges",
                "Organizations already in the Siemens ecosystem (Teamcenter, Opcenter MES)",
                "Manufacturers who need a dedicated scheduler separate from their planning platform",
            ],
            "ote_relationship": "Long-standing implementation partner",
        },
        "delmia_ortems": {
            "full_name": "DELMIA Ortems (Dassault Systemes)",
            "category": "Production scheduling within the 3DEXPERIENCE platform",
            "architecture": "Cloud (3DEXPERIENCE) and on-premise options",
            "sweet_spot": (
                "Process and hybrid manufacturers, particularly in industries "
                "with complex batch scheduling (pharma, food, chemical). Also "
                "strong for organizations invested in the Dassault ecosystem."
            ),
            "strengths": [
                "Strong process manufacturing capabilities: batch scheduling, campaign planning, tank/vessel management",
                "Three integrated modules: Manufacturing Planner (long-term), Production Scheduler (mid-term), "
                "Shop Floor Scheduler (short-term)",
                "Tight integration with DELMIA MES and ENOVIA (PLM) in the 3DEXPERIENCE platform",
                "Good visualization and scenario comparison tools",
                "Strong in pharma, food & beverage, and chemical industries",
                "Supports synchronization across multiple plants",
            ],
            "weaknesses": [
                "Strongest when deployed within the Dassault 3DEXPERIENCE ecosystem — value diminishes outside it",
                "Complex licensing and deployment model",
                "Smaller partner ecosystem compared to Kinaxis or Siemens",
                "Learning curve can be steep for organizations new to Dassault tools",
            ],
            "best_for": [
                "Process manufacturers (pharma, food, chemical) with batch scheduling needs",
                "Organizations already on the Dassault 3DEXPERIENCE platform",
                "Manufacturers needing tight PLM-to-scheduling integration (digital thread)",
                "Multi-plant synchronization in process industries",
            ],
            "ote_relationship": "Implementation partner",
        },
        "planet_together": {
            "full_name": "PlanetTogether APS",
            "category": "Mid-market APS focused on ease of use",
            "architecture": "Cloud and on-premise, web-based UI",
            "sweet_spot": (
                "Small-to-mid-market manufacturers who need finite capacity "
                "scheduling without the complexity and cost of enterprise APS "
                "platforms. Known for fast implementations and ERP-agnostic "
                "integration."
            ),
            "strengths": [
                "Fast implementation timelines (weeks, not months)",
                "ERP-agnostic: pre-built integrations with SAP, Oracle, Microsoft Dynamics, Epicor, IQMS, and more",
                "Intuitive UI — lower learning curve for schedulers",
                "Good balance of scheduling capability and simplicity",
                "Affordable for mid-market (lower TCO than enterprise platforms)",
                "Strong constraint-based scheduling and what-if analysis",
                "Web-based architecture supports remote scheduling",
            ],
            "weaknesses": [
                "Less sophisticated optimization algorithms than Opcenter or Ortems for very complex environments",
                "Limited S&OP/demand planning capabilities — focused on scheduling",
                "May lack depth for highly complex process manufacturing (batch/campaign)",
                "Smaller company — fewer global implementation resources than Siemens or Dassault",
            ],
            "best_for": [
                "Mid-market discrete manufacturers seeking first APS implementation",
                "Organizations wanting fast time-to-value without enterprise complexity",
                "Multi-ERP environments (acquisitions, diverse plant systems)",
                "Plants that need a scheduler the team can learn and own quickly",
            ],
            "ote_relationship": "Implementation partner",
        },
    },
    "selection_framework": {
        "description": (
            "Vendor selection should be driven by the manufacturer's specific "
            "requirements, not vendor reputation or marketing. OTE's vendor-agnostic "
            "approach uses a structured evaluation that considers:"
        ),
        "evaluation_dimensions": [
            {
                "dimension": "Production type fit",
                "description": (
                    "Discrete, process, or hybrid? Job shop, flow shop, or mixed? "
                    "Make-to-stock, make-to-order, engineer-to-order, or assemble-to-order? "
                    "Each production type has different scheduling requirements."
                ),
            },
            {
                "dimension": "Scheduling complexity",
                "description": (
                    "Number of resources, constraint types (sequence-dependent setups, "
                    "tooling, labor skills, material, tanks/vessels), optimization "
                    "objectives, rescheduling frequency."
                ),
            },
            {
                "dimension": "Planning scope",
                "description": (
                    "Do you need scheduling only, or also S&OP, demand planning, "
                    "and inventory optimization? A dedicated scheduler (Opcenter, "
                    "PlanetTogether) vs. a platform (Kinaxis, SAP IBP) depends on "
                    "this scope."
                ),
            },
            {
                "dimension": "ERP and MES ecosystem",
                "description": (
                    "What ERP and MES systems are in place? Siemens APS integrates "
                    "most naturally with Siemens MES and PLM. DELMIA Ortems with "
                    "Dassault. Kinaxis is ERP-agnostic. PlanetTogether has broad "
                    "pre-built connectors."
                ),
            },
            {
                "dimension": "Organizational maturity",
                "description": (
                    "First APS implementation or upgrade from an existing tool? "
                    "Data quality readiness? Change management capacity? A complex "
                    "tool in an immature organization is a recipe for failure."
                ),
            },
            {
                "dimension": "Scale and budget",
                "description": (
                    "Single plant or global multi-site rollout? The enterprise "
                    "platforms (Kinaxis, Siemens, DELMIA) justify their higher TCO "
                    "at scale. PlanetTogether offers a pragmatic entry point for "
                    "smaller operations."
                ),
            },
            {
                "dimension": "Internal capability",
                "description": (
                    "Will you have dedicated schedulers? IT resources for "
                    "integration and maintenance? The simplicity vs. power "
                    "trade-off depends on who will operate and maintain the system."
                ),
            },
        ],
    },
    "broader_landscape_context": {
        "other_notable_vendors": [
            {
                "vendor": "SAP IBP / SAP APO / SAP PP/DS",
                "note": (
                    "SAP's own planning and scheduling stack. PP/DS provides "
                    "finite scheduling within the SAP ecosystem. IBP is the "
                    "cloud-based S&OP/demand planning successor to APO. Strongest "
                    "for SAP-centric organizations but can be complex and expensive."
                ),
            },
            {
                "vendor": "Oracle Cloud SCM Planning",
                "note": (
                    "Oracle's cloud planning suite covering demand, supply, and "
                    "production planning. Strong for Oracle ERP customers. "
                    "Scheduling depth varies by module."
                ),
            },
            {
                "vendor": "Blue Yonder (JDA / Manugistics / i2)",
                "note": (
                    "Historically dominant in retail supply chain. Strong demand "
                    "planning and fulfillment. Manufacturing scheduling capabilities "
                    "less differentiated than dedicated APS tools."
                ),
            },
            {
                "vendor": "o9 Solutions",
                "note": (
                    "AI-native planning platform with strong demand sensing and "
                    "S&OP capabilities. Newer entrant disrupting traditional "
                    "planning vendors. Less mature in detailed shop-floor scheduling."
                ),
            },
            {
                "vendor": "Optessa (now Eyelit Technologies)",
                "note": (
                    "Niche strength in complex automotive and electronics sequencing. "
                    "Strong mathematical optimization. OTE partner."
                ),
            },
            {
                "vendor": "Greycon",
                "note": (
                    "Specialized in paper, metals, film, and other continuous process "
                    "industries. Strong trim and cut optimization. OTE partner."
                ),
            },
        ],
    },
}


# ============================================================================
# 8. MANUFACTURING METHODOLOGIES
# ============================================================================

MANUFACTURING_METHODOLOGIES: Dict[str, Any] = {
    "overview": (
        "Manufacturing methodologies provide the operational philosophy and "
        "improvement frameworks within which scheduling operates. A scheduling "
        "system does not exist in a vacuum — it reflects and supports the "
        "manufacturing strategy. Understanding these methodologies is essential "
        "for an implementation consultant because the client's operational "
        "philosophy shapes how the APS should be configured, what constraints "
        "to prioritize, and what KPIs to optimize."
    ),
    "methodologies": {
        "theory_of_constraints": {
            "name": "Theory of Constraints (TOC)",
            "originator": "Eli Goldratt (The Goal, 1984)",
            "core_principle": (
                "Every system has at least one constraint (bottleneck) that "
                "limits the system's output. Improving anything other than the "
                "constraint does not improve system throughput. Therefore: "
                "identify the constraint, exploit it (maximize its utilization), "
                "subordinate everything else to it, elevate it (invest to "
                "increase its capacity), and repeat."
            ),
            "five_focusing_steps": [
                "IDENTIFY the system's constraint (the resource with the least capacity relative to demand)",
                "EXPLOIT the constraint (ensure it is never idle — buffer it, prioritize its queue)",
                "SUBORDINATE everything else to the constraint (non-bottleneck resources run at the constraint's pace)",
                "ELEVATE the constraint (invest in additional capacity only if exploitation is maxed out)",
                "REPEAT — when the constraint shifts, start over with the new constraint",
            ],
            "scheduling_methodology": {
                "name": "Drum-Buffer-Rope (DBR)",
                "drum": (
                    "The constraint resource sets the pace (the drum) for the "
                    "entire production system. Its schedule IS the master schedule."
                ),
                "buffer": (
                    "Time buffers protect the constraint from upstream variability. "
                    "Material arrives at the constraint early enough to ensure it "
                    "is never starved. Buffer management monitors buffer penetration "
                    "to prioritize actions."
                ),
                "rope": (
                    "Material release is tied to the constraint's consumption rate "
                    "(the rope). You do not release material faster than the "
                    "constraint can consume it, preventing WIP accumulation."
                ),
            },
            "scheduling_intersection": [
                "APS should be configured to schedule the bottleneck first, then subordinate other resources",
                "Setup optimization at the bottleneck is highest priority (every minute of setup is lost throughput)",
                "Non-bottleneck resources should have protective capacity (planned underutilization)",
                "Buffer management provides early warning of schedule risk before due dates are missed",
                "WIP limits and material release controls prevent overloading the system",
            ],
            "ote_relevance": (
                "TOC is foundational to OTE's methodology. Their approach to APS "
                "implementation begins with identifying the binding constraint "
                "and building the schedule around it. This is explicitly called "
                "out in the brand positioning and the MDIF framework."
            ),
        },
        "lean_manufacturing": {
            "name": "Lean Manufacturing / Toyota Production System (TPS)",
            "originator": "Taiichi Ohno, Shigeo Shingo (Toyota, 1950s-1970s)",
            "core_principle": (
                "Eliminate waste (muda) in all forms — overproduction, waiting, "
                "transport, over-processing, inventory, motion, defects. Create "
                "flow by producing only what the customer needs, when they need "
                "it, in the quantity needed."
            ),
            "key_concepts": [
                {
                    "concept": "Just-in-Time (JIT)",
                    "description": (
                        "Produce and deliver the right items at the right time in "
                        "the right amount. Minimizes inventory and WIP. Requires "
                        "reliable processes and short changeover times."
                    ),
                },
                {
                    "concept": "Kanban (pull system)",
                    "description": (
                        "Signal-based production control where downstream processes "
                        "pull from upstream. The scheduling implication: production "
                        "is triggered by consumption, not by a push-based schedule."
                    ),
                },
                {
                    "concept": "Heijunka (production leveling)",
                    "description": (
                        "Smooth production volume and mix over time to reduce "
                        "variability. Instead of making all of Product A Monday "
                        "and all of Product B Tuesday, make a mix of both every day. "
                        "This has direct scheduling implications for sequence planning."
                    ),
                },
                {
                    "concept": "SMED (Single-Minute Exchange of Dies)",
                    "description": (
                        "Systematic reduction of setup/changeover time. Directly "
                        "impacts scheduling: shorter setups enable smaller batches, "
                        "more changeovers, and more flexibility."
                    ),
                },
                {
                    "concept": "Jidoka (autonomation)",
                    "description": (
                        "Machines detect defects and stop automatically. Prevents "
                        "defective WIP from propagating through the schedule."
                    ),
                },
                {
                    "concept": "Kaizen (continuous improvement)",
                    "description": (
                        "Incremental, ongoing improvement. In scheduling context: "
                        "continuously refining the model, parameters, and constraints "
                        "based on actual performance data."
                    ),
                },
            ],
            "scheduling_intersection": [
                "Lean environments may use pull-based scheduling (kanban) instead of push-based APS for repetitive production",
                "APS is most valuable in lean environments for complex, mixed-model, or job-shop scenarios where pure kanban breaks down",
                "Heijunka principles can be encoded in the APS as leveling constraints",
                "SMED improvements should be reflected in updated setup times in the APS model",
                "APS can optimize the tension between batch size (efficiency) and small lots (lean flow)",
                "Lean metrics (takt time, cycle time, WIP limits) become scheduling parameters in the APS",
            ],
            "tension_with_scheduling": (
                "There is a philosophical tension between lean (minimize everything, "
                "let flow pull) and APS (centrally optimize a schedule). In practice, "
                "most manufacturers need both: kanban for simple, repetitive flows "
                "and APS for complex, variable, constraint-heavy scheduling. The "
                "art is knowing where each approach applies."
            ),
        },
        "six_sigma": {
            "name": "Six Sigma",
            "originator": "Bill Smith (Motorola, 1986), popularized by GE",
            "core_principle": (
                "Reduce process variation using statistical methods. A Six Sigma "
                "process produces no more than 3.4 defects per million opportunities. "
                "Follows the DMAIC cycle: Define, Measure, Analyze, Improve, Control."
            ),
            "scheduling_intersection": [
                "Reduced process variation means more predictable cycle times, which makes scheduling more accurate",
                "Statistical process control (SPC) data feeds scheduling parameter calibration",
                "DMAIC projects on bottleneck processes directly improve scheduling capacity",
                "Yield improvement from Six Sigma projects reduces the scrap factor in scheduling calculations",
                "Control phase often involves updating scheduling parameters to reflect the improved process",
            ],
            "combined_with_toc": (
                "The TLS (TOC-Lean-Six Sigma) integration applies Six Sigma "
                "specifically to the constraint identified by TOC and streamlined "
                "by Lean. OTE references TLS in their methodology — optimize the "
                "binding constraint, then apply Six Sigma to reduce its variability."
            ),
        },
        "agile_manufacturing": {
            "name": "Agile Manufacturing",
            "core_principle": (
                "The ability to rapidly reconfigure production capabilities to "
                "respond to changing market demands, customization requirements, "
                "and unpredictable disruptions. Emphasizes responsiveness, "
                "flexibility, and speed-to-market."
            ),
            "scheduling_intersection": [
                "APS enables agility by providing rapid rescheduling capability",
                "What-if scenarios allow evaluation of responses to demand changes",
                "Alternate routing and resource modeling supports flexible manufacturing",
                "Short planning cycles and reactive scheduling are core agile scheduling patterns",
                "Digital twins allow simulation of response options before committing",
            ],
            "contrast_with_lean": (
                "Lean optimizes for efficiency in stable demand environments. Agile "
                "optimizes for responsiveness in volatile demand environments. "
                "Many manufacturers need 'leagile' — lean for base demand, agile "
                "for demand variability."
            ),
        },
        "industry_4_0": {
            "name": "Industry 4.0 / Smart Manufacturing",
            "core_principle": (
                "The integration of cyber-physical systems, IoT, cloud computing, "
                "AI/ML, and advanced analytics into manufacturing to create "
                "intelligent, self-optimizing production systems. Also known as "
                "the Fourth Industrial Revolution."
            ),
            "key_technologies": [
                "Industrial Internet of Things (IIoT) — sensors and connected devices",
                "Cyber-physical systems (CPS) — digital models linked to physical assets",
                "Cloud and edge computing — scalable, distributed computation",
                "Artificial intelligence and machine learning — pattern recognition and optimization",
                "Digital twins — virtual replicas for simulation and analysis",
                "Additive manufacturing (3D printing) — flexible production without tooling",
                "Augmented reality (AR) — operator guidance and training",
                "Blockchain — supply chain traceability and provenance",
                "5G — low-latency, high-bandwidth factory communications",
            ],
            "scheduling_intersection": [
                "IIoT provides real-time data that makes schedules more accurate and responsive",
                "Digital twins enable simulation-based scheduling optimization",
                "AI/ML can optimize scheduling decisions beyond human or rule-based capability",
                "Edge computing enables real-time scheduling adjustments at the machine level",
                "Connected supply chains enable multi-tier scheduling visibility",
                "Predictive analytics reduce unplanned downtime that disrupts schedules",
            ],
            "standards_and_frameworks": [
                {
                    "name": "ISA-95 / IEC 62264",
                    "description": "Enterprise-control system integration standard. Defines the layers and data models for IT/OT integration.",
                },
                {
                    "name": "ISA-88 / IEC 61512",
                    "description": "Batch control standard. Defines equipment models, recipes, and control structures for process manufacturing.",
                },
                {
                    "name": "OPC-UA",
                    "description": "Platform-independent communication standard for industrial automation. Enables machine-to-cloud data flow.",
                },
                {
                    "name": "CESMII Smart Manufacturing Profile",
                    "description": "Standardized information model for smart manufacturing data interoperability. OTE is a CESMII partner.",
                },
                {
                    "name": "WEF Global Lighthouse Network",
                    "description": (
                        "World Economic Forum recognition of factories leading Industry 4.0 adoption. "
                        "OTE's top-5 life sciences client selected them using the Lighthouse framework."
                    ),
                },
            ],
            "ote_relevance": (
                "Smart Manufacturing is central to OTE's post-merger identity. "
                "The Toward Zero heritage brings ISA-95/88 expertise, CESMII "
                "partnership, and OT integration capability. The MDIF framework "
                "is explicitly positioned as an Industry 4.0 enablement methodology."
            ),
        },
    },
    "methodology_selection_guidance": (
        "These methodologies are not mutually exclusive. Most manufacturers "
        "employ elements of several simultaneously:\n\n"
        "- TOC: Use when the operation has a clear bottleneck and throughput is "
        "the primary metric. This is where scheduling has the most impact.\n"
        "- Lean: Use for repetitive, stable-demand production lines. May reduce "
        "the need for APS in simple flows (kanban suffices).\n"
        "- Six Sigma: Use alongside TOC to reduce variability at the constraint. "
        "Improves scheduling reliability.\n"
        "- Agile: Use when demand volatility is high and responsiveness is "
        "competitive. APS enables agile manufacturing through rapid rescheduling.\n"
        "- Industry 4.0: Use as the technology enablement layer. Provides the "
        "data foundation that makes sophisticated scheduling possible.\n\n"
        "For OTE implementation consultants, the question is not 'which methodology?' "
        "but 'what is the client's operational philosophy, and how should the APS "
        "be configured to support it?' A lean plant needs different scheduling "
        "logic (leveling, small lots, pull signals) than a TOC plant (bottleneck-first, "
        "buffer management, DBR) or an agile plant (rapid rescheduling, alternate "
        "routings, what-if scenarios)."
    ),
}


# ============================================================================
# COMPOSITE KNOWLEDGE BASE
# ============================================================================

DOMAIN_KNOWLEDGE: Dict[str, Any] = {
    "planning_hierarchy": PLANNING_HIERARCHY,
    "sop_ibp": SOP_IBP,
    "mrp_mps": MRP_MPS,
    "execution": EXECUTION,
    "digital_transformation": DIGITAL_TRANSFORMATION,
    "aps_failure_modes": APS_FAILURE_MODES,
    "vendor_landscape": VENDOR_LANDSCAPE,
    "manufacturing_methodologies": MANUFACTURING_METHODOLOGIES,
    "metadata": {
        "version": "1.0.0",
        "scope": (
            "Supply chain planning and execution domain knowledge for "
            "On Time Edge implementation consultants."
        ),
        "sections": [
            "planning_hierarchy",
            "sop_ibp",
            "mrp_mps",
            "execution",
            "digital_transformation",
            "aps_failure_modes",
            "vendor_landscape",
            "manufacturing_methodologies",
        ],
        "usage_notes": (
            "This module is designed to be consumed programmatically. All data "
            "is stored in Python dictionaries and lists, serializable to JSON. "
            "Access via DOMAIN_KNOWLEDGE['section_name'] or import individual "
            "section constants directly."
        ),
    },
}


# ============================================================================
# CONVENIENCE ACCESSORS
# ============================================================================


def get_section(name: str) -> Dict[str, Any]:
    """Return a top-level section by name. Raises KeyError if not found."""
    return DOMAIN_KNOWLEDGE[name]


def get_all_sections() -> List[str]:
    """Return the list of available section names."""
    return DOMAIN_KNOWLEDGE["metadata"]["sections"]


def get_planning_level(level: str) -> Dict[str, Any]:
    """Return a specific planning hierarchy level (strategic, tactical, operational, execution)."""
    return PLANNING_HIERARCHY["levels"][level]


def get_vendor(vendor_key: str) -> Dict[str, Any]:
    """Return vendor details by key (e.g., 'kinaxis_maestro', 'siemens_opcenter_aps')."""
    return VENDOR_LANDSCAPE["vendors"][vendor_key]


def get_failure_modes_by_category(category: str) -> List[Dict[str, Any]]:
    """Return all APS failure modes for a given category (e.g., 'Data Quality', 'Change Management')."""
    return [
        fm
        for fm in APS_FAILURE_MODES["failure_modes"]
        if fm["category"].lower() == category.lower()
    ]


def get_methodology(name: str) -> Dict[str, Any]:
    """Return a manufacturing methodology by key (e.g., 'theory_of_constraints', 'lean_manufacturing')."""
    return MANUFACTURING_METHODOLOGIES["methodologies"][name]


def search_knowledge(keyword: str) -> List[Dict[str, str]]:
    """
    Search across all sections for a keyword (case-insensitive).
    Returns a list of dicts with 'section', 'path', and 'snippet'.
    Useful for building context-aware prompts.
    """
    results: List[Dict[str, str]] = []
    keyword_lower = keyword.lower()

    def _walk(obj: Any, section: str, path: str) -> None:
        if isinstance(obj, str):
            if keyword_lower in obj.lower():
                snippet = obj[:200] + ("..." if len(obj) > 200 else "")
                results.append(
                    {
                        "section": section,
                        "path": path,
                        "snippet": snippet,
                    }
                )
        elif isinstance(obj, dict):
            for k, v in obj.items():
                _walk(v, section, f"{path}.{k}" if path else k)
        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                _walk(item, section, f"{path}[{i}]")

    for section_name in get_all_sections():
        _walk(DOMAIN_KNOWLEDGE[section_name], section_name, "")

    return results
