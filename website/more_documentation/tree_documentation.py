from nicegui import ui

from ..documentation_tools import text_demo


def main_demo() -> None:
    ui.tree([
        {'id': 'numbers', 'children': [{'id': '1'}, {'id': '2'}]},
        {'id': 'letters', 'children': [{'id': 'A'}, {'id': 'B'}]},
    ], label_key='id', on_select=lambda e: ui.notify(e.value))


def more() -> None:
    @text_demo('Tree with custom header and body', '''
        Scoped slots can be used to insert custom content into the header and body of a tree node.
        See the [Quasar documentation](https://quasar.dev/vue-components/tree#customize-content) for more information.
    ''')
    def tree_with_custom_header_and_body():
        tree = ui.tree([
            {'id': 'numbers', 'description': 'Just some numbers', 'children': [
                {'id': '1', 'description': 'The first number'},
                {'id': '2', 'description': 'The second number'},
            ]},
            {'id': 'letters', 'description': 'Some latin letters', 'children': [
                {'id': 'A', 'description': 'The first letter'},
                {'id': 'B', 'description': 'The second letter'},
            ]},
        ], label_key='id', on_select=lambda e: ui.notify(e.value))

        tree.add_slot('default-header', '''
            <span :props="props">Node <strong>{{ props.node.id }}</strong></span>
        ''')
        tree.add_slot('default-body', '''
            <span :props="props">Description: "{{ props.node.description }}"</span>
        ''')
