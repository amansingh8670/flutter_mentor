# ==========================================================
# IMPLEMENTATION PLAN MODEL
# ==========================================================

from dataclasses import dataclass, field


# ==========================================================
# REUSABLE WIDGET
# ==========================================================

@dataclass
class ReusableWidget:

    name: str
    file: str
    reason: str


# ==========================================================
# LAYOUT NODE
# ==========================================================

@dataclass
class LayoutNode:

    widget: str

    children: list["LayoutNode"] = field(
        default_factory=list
    )


# ==========================================================
# LAYOUT
# ==========================================================

@dataclass
class Layout:

    root: str

    body: list[LayoutNode] = field(
        default_factory=list
    )


# ==========================================================
# IMPLEMENTATION PLAN
# ==========================================================

@dataclass
class ImplementationPlan:

    # Short summary of the screen
    screen_summary: str

    # Existing reusable widgets
    reuse_widgets: list[ReusableWidget]

    # Existing files to edit
    modify_files: list[str]

    # New files to create
    new_files: list[str]

    # Planned widget tree
    layout: Layout

    # Architecture decisions
    architecture_notes: list[str]

    # Planner detected missing reusable components
    missing_components: list[str] = field(
        default_factory=list
    )

    # Overall implementation steps
    implementation_steps: list[str] = field(
        default_factory=list
    )

    # Potential risks / assumptions
    assumptions: list[str] = field(
        default_factory=list
    )


# ==========================================================
# LAYOUT PARSER
# ==========================================================

def parse_layout_node(
    data: dict,
) -> LayoutNode:

    return LayoutNode(

        widget=data.get(
            "widget",
            "",
        ),

        children=[

            parse_layout_node(child)

            for child in data.get(
                "children",
                [],
            )

        ],
    )


# ==========================================================
# JSON PARSER
# ==========================================================

def implementation_plan_from_json(
    data: dict,
) -> ImplementationPlan:

    layout_data = data.get(
        "layout",
        {},
    )

    return ImplementationPlan(

        screen_summary=data.get(
            "screen_summary",
            "",
        ),

        reuse_widgets=[

            ReusableWidget(

                name=item.get(
                    "name",
                    "",
                ),

                file=item.get(
                    "file",
                    "",
                ),

                reason=item.get(
                    "reason",
                    "",
                ),

            )

            for item in data.get(
                "reuse_widgets",
                [],
            )

        ],

        modify_files=data.get(
            "modify_files",
            [],
        ),

        new_files=data.get(
            "new_files",
            [],
        ),

        layout=Layout(

            root=layout_data.get(
                "root",
                "",
            ),

            body=[

                parse_layout_node(node)

                for node in layout_data.get(
                    "body",
                    [],
                )

            ],

        ),

        architecture_notes=data.get(
            "architecture_notes",
            [],
        ),

        missing_components=data.get(
            "missing_components",
            [],
        ),

        implementation_steps=data.get(
            "implementation_steps",
            [],
        ),

        assumptions=data.get(
            "assumptions",
            [],
        ),

    )