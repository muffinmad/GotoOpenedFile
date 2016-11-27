import sublime
import sublime_plugin
import os


goto_opened_file_opened = False
active_view = None


class GotoOpenedFile(sublime_plugin.WindowCommand):

    def _get_view_item(self, view):
        if view['view'].file_name():
            result = [
                os.path.basename(view['view'].file_name()),
                view['view'].file_name()[self.common_path_len:]
            ]
        elif view['view'].name():
            result = [
                view['view'].name(),
                view['view'].name()
            ]
        else:
            result = ['untitled', 'untitled']
        if self.num_groups > 1:
            result.append('Group: {}'.format(view['group'] + 1))
        return result

    def on_done(self, idx):
        global goto_opened_file_opened
        goto_opened_file_opened = False
        if idx == -1:
            global active_view
            if active_view:
                self.window.focus_view(active_view)
        else:
            v = self.views[idx]
            if v['group'] != self.active_group:
                self.window.focus_view(v['view'])

    def on_highlighted(self, idx):
        if idx > -1:
            v = self.views[idx]
            if v['group'] == self.active_group:
                self.window.focus_view(v['view'])
            else:
                global active_view
                if active_view in self.window.views_in_group(self.active_group):
                    self.window.focus_view(active_view)

    def get_views_in_group(self, group):
        return map(lambda x: {'group': group, 'view': x}, self.window.views_in_group(group))

    def run(self):
        global goto_opened_file_opened
        global active_view
        active_view = self.window.active_view()
        self.active_group = self.window.active_group()
        if len(self.window.views_in_group(self.active_group)) and len(self.window.views()) > 1:
            self.num_groups = self.window.num_groups()
            self.views = []
            for x in range(self.num_groups):
                self.views.extend(self.get_views_in_group(x))
            self.common_path = os.path.commonprefix(list(filter(bool, map(lambda x: x['view'].file_name(), self.views))))
            self.common_path_len = len(self.common_path)
            self.views_items = list(map(self._get_view_item, self.views))
            goto_opened_file_opened = True
            active_view_idx = -1
            for x in range(len(self.views)):
                if self.views[x]['view'] == active_view:
                    active_view_idx = x
                    break
            self.window.show_quick_panel(
                self.views_items,
                self.on_done,
                sublime.KEEP_OPEN_ON_FOCUS_LOST,
                active_view_idx,
                self.on_highlighted)
        else:
            self.window.run_command('show_overlay', {'overlay': 'goto', 'show_files': True})


class GotoAnyFileCommand(sublime_plugin.WindowCommand):

    def run(self):
        global active_view
        w = self.window
        if active_view:
            w.focus_view(active_view)
        w.run_command('show_overlay', {'overlay': 'goto', 'show_files': True})


class CtrlPEventListener(sublime_plugin.EventListener):

    def on_query_context(self, view, key, operator, operand, match_all):
        if key != 'goto_opened_opened':
            return None
        global goto_opened_file_opened
        if operator == sublime.OP_EQUAL:
            return operand == goto_opened_file_opened
        if operator == sublime.OP_NOT_EQUAL:
            return operand != goto_opened_file_opened
        return False
