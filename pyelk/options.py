"""Layout options parsing and management for ELK."""
import re
import copy
from typing import Any, Dict, Optional


# Default layout option values
DEFAULTS = {
    'elk.direction': 'RIGHT',
    'elk.padding': '[left=12, top=12, right=12, bottom=12]',
    'elk.spacing.nodeNode': 20.0,
    'elk.layered.spacing.nodeNodeBetweenLayers': 20.0,
    'elk.spacing.edgeNode': 10.0,
    'elk.spacing.edgeEdge': 10.0,
    'elk.layered.spacing.edgeNodeBetweenLayers': 10.0,
    'elk.layered.spacing.edgeEdgeBetweenLayers': 10.0,
    'elk.nodeLabels.placement': '',
    'elk.portConstraints': 'UNDEFINED',
    'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
    'elk.layered.layering.strategy': 'LONGEST_PATH',
    'elk.hierarchyHandling': 'SEPARATE_CHILDREN',
}

# Aliases: short names to full qualified names
ALIASES = {
    'algorithm': 'elk.algorithm',
    'direction': 'elk.direction',
    'spacing': 'elk.spacing.nodeNode',
    'layering.strategy': 'elk.layered.layering.strategy',
    'hierarchyHandling': 'elk.hierarchyHandling',
    'portConstraints': 'elk.portConstraints',
    'port.side': 'elk.port.side',
    'port.index': 'elk.port.index',
    'layerConstraint': 'elk.layered.layering.layerConstraint',
    'position': 'elk.position',
    'bendPoints': 'elk.bendPoints',
}

# Algorithm name aliases
ALGORITHM_ALIASES = {
    'layered': 'org.eclipse.elk.layered',
    'elk.layered': 'org.eclipse.elk.layered',
    'stress': 'org.eclipse.elk.stress',
    'elk.stress': 'org.eclipse.elk.stress',
    'mrtree': 'org.eclipse.elk.mrtree',
    'elk.mrtree': 'org.eclipse.elk.mrtree',
    'radial': 'org.eclipse.elk.radial',
    'elk.radial': 'org.eclipse.elk.radial',
    'force': 'org.eclipse.elk.force',
    'elk.force': 'org.eclipse.elk.force',
    'disco': 'org.eclipse.elk.disco',
    'elk.disco': 'org.eclipse.elk.disco',
    'sporeOverlap': 'org.eclipse.elk.sporeOverlap',
    'elk.sporeOverlap': 'org.eclipse.elk.sporeOverlap',
    'sporeCompaction': 'org.eclipse.elk.sporeCompaction',
    'elk.sporeCompaction': 'org.eclipse.elk.sporeCompaction',
    'rectpacking': 'org.eclipse.elk.rectpacking',
    'elk.rectpacking': 'org.eclipse.elk.rectpacking',
    'fixed': 'org.eclipse.elk.fixed',
    'elk.fixed': 'org.eclipse.elk.fixed',
}


def resolve_algorithm(name: Optional[str]) -> str:
    """Resolve an algorithm name to its full qualified name."""
    if name is None:
        return 'org.eclipse.elk.layered'
    if name in ALGORITHM_ALIASES:
        return ALGORITHM_ALIASES[name]
    if name.startswith('org.eclipse.elk.'):
        return name
    return name


def resolve_option_key(key: str) -> str:
    """Resolve an option key, expanding aliases and prefixes."""
    if key in ALIASES:
        return ALIASES[key]
    # Add org.eclipse. prefix handling
    if key.startswith('org.eclipse.elk.'):
        short = key[len('org.eclipse.'):]
        return short
    return key


def parse_padding(value: str) -> Dict[str, float]:
    """Parse ELK padding format: '[left=2, top=3, right=3, bottom=2]' or 'top=X, ...'."""
    result = {'top': 0.0, 'bottom': 0.0, 'left': 0.0, 'right': 0.0}
    # Strip brackets
    s = value.strip()
    if s.startswith('['):
        s = s[1:]
    if s.endswith(']'):
        s = s[:-1]
    # Parse key=value pairs
    for part in s.split(','):
        part = part.strip()
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip().lower()
            v = float(v.strip())
            if k in result:
                result[k] = v
    return result


def parse_kvector(value: str) -> Dict[str, float]:
    """Parse KVector format: '(23, 43)' -> {x: 23, y: 43}."""
    s = value.strip()
    if s.startswith('('):
        s = s[1:]
    if s.endswith(')'):
        s = s[:-1]
    parts = s.split(',')
    x = float(parts[0].strip())
    y = float(parts[1].strip())
    return {'x': x, 'y': y}


def parse_kvector_chain(value: str) -> list:
    """Parse KVectorChain format: '( {1,2}, {3,4} )' -> [{x:1,y:2}, {x:3,y:4}]."""
    s = value.strip()
    # Remove outer parens
    if s.startswith('('):
        s = s[1:]
    if s.endswith(')'):
        s = s[:-1]
    s = s.strip()
    result = []
    # Find all {x,y} pairs
    for m in re.finditer(r'\{([^}]+)\}', s):
        inner = m.group(1)
        parts = inner.split(',')
        x = float(parts[0].strip())
        y = float(parts[1].strip())
        result.append({'x': x, 'y': y})
    return result


def get_option(element: dict, key: str, default=None) -> Any:
    """Get a layout option from an element, checking both layoutOptions and properties."""
    resolved = resolve_option_key(key)

    # Check layoutOptions first
    layout_opts = element.get('layoutOptions', {})
    if layout_opts:
        if key in layout_opts:
            return layout_opts[key]
        if resolved in layout_opts:
            return layout_opts[resolved]
        # Check with org.eclipse prefix
        full_key = 'org.eclipse.' + resolved if not resolved.startswith('org.eclipse.') else resolved
        if full_key in layout_opts:
            return layout_opts[full_key]

    # Check properties (alternative name used in some graph formats)
    props = element.get('properties', {})
    if props:
        if key in props:
            return props[key]
        if resolved in props:
            return props[resolved]
        full_key = 'org.eclipse.' + resolved if not resolved.startswith('org.eclipse.') else resolved
        if full_key in layout_opts:
            return layout_opts[full_key]
        if full_key in props:
            return props[full_key]

    return default


def merge_options(base: dict, override: dict) -> dict:
    """Merge layout options, with override taking precedence."""
    result = dict(base)
    for k, v in override.items():
        result[k] = v
    return result


def get_effective_options(element: dict, global_options: Optional[dict] = None,
                          parent_options: Optional[dict] = None) -> dict:
    """Get the effective layout options for an element, considering inheritance."""
    result = {}

    # Start with global options
    if global_options:
        result.update(global_options)

    # Add parent options (inherited)
    if parent_options:
        result.update(parent_options)

    # Element's own options override everything (both layoutOptions and properties)
    own_opts = element.get('layoutOptions', {})
    if own_opts:
        result.update(own_opts)
    own_props = element.get('properties', {})
    if own_props:
        result.update(own_props)

    return result


def get_algorithm(element: dict, global_options: Optional[dict] = None) -> str:
    """Get the resolved algorithm for an element."""
    # Check element's own options first
    alg = get_option(element, 'algorithm')
    if alg is None and global_options:
        alg = global_options.get('algorithm') or global_options.get('elk.algorithm')
    if alg is None:
        alg = 'layered'
    return resolve_algorithm(alg)


def get_direction(element: dict, global_options: Optional[dict] = None) -> str:
    """Get the layout direction."""
    d = get_option(element, 'elk.direction')
    if d is None and global_options:
        d = global_options.get('elk.direction') or global_options.get('direction')
    if d is None:
        d = 'DOWN'
    return d


def get_spacing(element: dict, key: str, global_options: Optional[dict] = None,
                default: float = 20.0) -> float:
    """Get a spacing value."""
    val = get_option(element, key)
    if val is None and global_options:
        resolved = resolve_option_key(key)
        val = global_options.get(key) or global_options.get(resolved)
        if val is None:
            full = 'org.eclipse.' + resolved if not resolved.startswith('org.eclipse.') else resolved
            val = global_options.get(full)
    if val is not None:
        return float(val)
    return default


def get_padding(element: dict, global_options: Optional[dict] = None) -> Dict[str, float]:
    """Get the padding for an element."""
    val = get_option(element, 'elk.padding')
    if val is None and global_options:
        val = global_options.get('elk.padding') or global_options.get('org.eclipse.elk.padding')
    if val is None:
        val = DEFAULTS['elk.padding']
    if isinstance(val, str):
        return parse_padding(val)
    return val
