"""Layout algorithm implementations for ELK."""
from .fixed import FixedLayoutProvider
from .spore import SporeCompactionProvider, SporeOverlapProvider
from .rectpacking import RectPackingProvider
from .stress import StressLayoutProvider
from .force import ForceLayoutProvider
from .mrtree import MrTreeLayoutProvider
from .radial import RadialLayoutProvider
from .layered import LayeredLayoutProvider

ALGORITHM_REGISTRY = {
    'org.eclipse.elk.fixed': FixedLayoutProvider,
    'org.eclipse.elk.layered': LayeredLayoutProvider,
    'org.eclipse.elk.stress': StressLayoutProvider,
    'org.eclipse.elk.force': ForceLayoutProvider,
    'org.eclipse.elk.mrtree': MrTreeLayoutProvider,
    'org.eclipse.elk.radial': RadialLayoutProvider,
    'org.eclipse.elk.sporeCompaction': SporeCompactionProvider,
    'org.eclipse.elk.sporeOverlap': SporeOverlapProvider,
    'org.eclipse.elk.rectpacking': RectPackingProvider,
}


def get_layout_provider(algorithm_id: str):
    """Get a layout provider for the given algorithm ID."""
    if algorithm_id in ALGORITHM_REGISTRY:
        return ALGORITHM_REGISTRY[algorithm_id]()
    return None
