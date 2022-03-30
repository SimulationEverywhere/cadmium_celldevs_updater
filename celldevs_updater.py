from __future__ import annotations
import json


def celldevs_update(old_path: str, new_path: str | None = None):
    new_path = f'new_{old_path}' if new_path is None else new_path

    # We read the old JSON file
    with open(old_path) as f:
        old_config = json.load(f)
    old_scenario = old_config.pop('scenario', dict())
    old_cells = old_config.pop('cells', dict())

    new_scenario = {'shape': old_scenario['shape'], 'wrapped': old_scenario.get('wrapped', False)}
    new_cells = dict()
    new_cell_map = dict()

    # We extract the default cell config stuff
    new_default = dict()
    for new_config_key in 'delay', 'cell_type', 'state', 'config', 'neighborhood':
        old_config_key = f'default_{new_config_key}' if new_config_key != 'neighborhood' else new_config_key
        if old_config_key in old_scenario:
            new_default[new_config_key] = old_scenario.pop(old_config_key)
    new_cells['default'] = new_default

    # We find all the different configurations and build the cell_map
    config_n = 1
    for cell_config in old_cells:
        cell_id = cell_config.pop('cell_id')
        config_patch = compute_patch(new_cells['default'], cell_config)
        if not config_patch:
            continue
        cell_config_id = None
        for config_id, config in new_cells.items():  # TODO arreglar lo de default -> computar patches y compararlos
            if config_patch == config and config_id != 'default':
                cell_config_id = config_id
                break
        # If cell configuration is new, we need to create a new one
        if cell_config_id is None:
            cell_config_id = f'cell_{config_n}'
            config_n += 1
            new_cells[cell_config_id] = config_patch
            new_cell_map[cell_config_id] = list()
        new_cell_map[cell_config_id].append(cell_id)

    # We store the outcome in the new JSON file
    new_config = {**new_scenario, 'cells': new_cells, 'cell_map': new_cell_map}
    with open(new_path, 'w') as f:
        json.dump(new_config, f, indent=4)


def compute_patch(default_config: dict, cell_config: dict) -> dict:
    res = dict()
    for field_id, field_val in cell_config.items():
        default_val = default_config.get(field_id)
        if default_val != field_val:
            if isinstance(default_val, dict) and isinstance(field_val, dict):
                field_patch = compute_patch(default_val, field_val)
                if field_patch:
                    res[field_id] = field_patch
            else:
                res[field_id] = field_val
    return res


if __name__ == '__main__':
    old_format_file_path = 'old.json'
    new_format_file_path = 'new.json'
    celldevs_update(old_format_file_path, new_format_file_path)
