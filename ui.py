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
        # big thanks to @rstoro for replacing my buggy query with this beauty
        ans = db.execute('''
            with book_series as (
                select
                    b.id
                ,    bsl.series
                ,    b.series_index
                ,    r.rating
                ,    r.rating is not null as current_series_read
                ,    lag(r.rating) over(partition by bsl.series order by b.series_index asc) is not null as prior_series_read
                from
                    books as b
                inner join
                    books_series_link as bsl
                    on bsl.book = b.id
                left join
                    books_ratings_link as brl
                    on brl.book = b.id
                left join
                    ratings as r
                    on r.id = brl.rating
            ),

            started_series_books_to_read_next as (
                select
                    book_series.id
                ,    book_series.series
                ,    book_series.series_index
                ,    book_series.rating
                ,    row_number() over(partition by book_series.series order by book_series.series_index desc) as should_read_book_next
                from
                    book_series
                where
                    book_series.rating is null
                    and book_series.prior_series_read
            )

            select
                started_series_books_to_read_next.id
            from
                started_series_books_to_read_next
            where
                started_series_books_to_read_next.should_read_book_next = 1
            order by
                started_series_books_to_read_next.id asc
            ;
        ''')
        
        self.gui.current_db.set_marked_ids({
            row[0]:'readnext'
            for row in ans.fetchall()
        })

        # Tell the GUI to search for all marked records
        self.gui.search.setEditText('marked:readnext')
        self.gui.search.do_search()