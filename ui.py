import os
from calibre.gui2.actions import InterfaceAction


class InterfacePlugin(InterfaceAction):

    name = 'Read Next'
    action_spec = ('Read Next', None,
            'Mark the next unrated book in each series', None)

    def genesis(self):
        icon = get_icons('images/icon.png', 'ReadNext Plugin')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.mark_books)
        
    def mark_books(self):
        
        path = os.path.dirname(self.gui.current_db.dbpath)
        from calibre.db.backend import DB
        db = DB(path, read_only=True)
        
        # get one unrated book per series
        # where at least one other entry in the series has been rated
        ans = db.execute('''
        select id from (
        select *,
            row_number() over(
            partition by series order by series_index asc
            ) row_num
        from (
            select
            b.id, bsl.series, b.series_index, r.rating
            from books b
            inner join books_series_link bsl on b.id = bsl.book
            left join books_ratings_link brl on b.id = brl.book
            left join ratings r on brl.rating = r.id
        ) where rating is null
        )
        where row_num = 1 and series_index > 1
        ''')
        
        self.gui.current_db.set_marked_ids({
            row[0]:'readnext'
            for row in ans.fetchall()
        })

        # Tell the GUI to search for all marked records
        self.gui.search.setEditText('marked:readnext')
        self.gui.search.do_search()