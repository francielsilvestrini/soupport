# -*- coding: utf-8 -*-

def comments_list():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'        
        return dict(msg='comments/reply dont work!')

    def get_comments(t, k):
        clist = []
        query = ((db.comments.owner_table == t) & (db.comments.owner_key == k))
        for row in db(query).select():
            clist.append( (row, get_comments('comments', row.oplink)) )
        return clist 

    def html_comments(clist, is_reply):
        comments = []
        for (row, reply) in clist:
            reply_mark = SPAN(' ', T('reply'), _class='muted')
            remove_link = A(' '+T('Remove'), _href='javascript:void(0);', _id='comment_%s' % row.id, _class='remove-comment')
            dh_mark = SMALL([
                SPAN(prettydate(row.updated_on, T), _class='muted'),
                remove_link if row.updated_by == auth.user.id else ''] )
            right_wgt = DIV(dh_mark, _class='pull-right')            
            
            header_wgt = DIV(
                STRONG('%(first_name)s %(last_name)s' % db.auth_user[row.updated_by]),
                reply_mark if is_reply else '',
                right_wgt)

            reply_rows = html_comments(reply, True)

            hidden_wgt = INPUT(_id='owner_key', _value=row.oplink, _type='hidden')

            reply_link = DIV(
                A(T('Reply'), _href='javascript:void(0);', _class='reply-link'),
                hidden_wgt,
                _id='reply_%s' % row.id
                )
            comment_wgt = DIV(
                P(row.comment_str),
                reply_link,
                reply_rows
                )

            img_wgt = DIV(
                DIV(IMG(_src=get_user_photo_url(row.updated_by)), 
                    _style='width:64px; height:64px; max-width:64px; overflow:hidden;'),
                    _class='span1')
            body_wgt = DIV(
                header_wgt, 
                comment_wgt,
                _class='span11')
            row_wgt = DIV(img_wgt, body_wgt, _class='row-fluid')

            comments += [row_wgt]

        js = '''
            $(document).ready(function() {
                $(".reply-link").click(function () {
                    var parentTag = $( this ).parent();
                    var k = $(parentTag).find("#owner_key").val();
                    var url = '%(url_reply)s?reply='+k+'&wgt='+parentTag.get(0).id;
                    $.web2py.component(url, parentTag.get(0).id );
                });
                $(".reply-cancel").click(function () {
                    $.web2py.component('%(url_list)s','comments_list');
                });    
                $(".remove-comment").click(function () {
                    var str = $(this).get(0).id;
                    var id = str.split("_")[1];

                    var url = '%(url_remove)s';
                    ajax(url + '?delete=' + id, [], '');
                });
            });             
            ''' % {
                'url_remove':URL(c='comments', f='comments_remove', args=[owner_table, owner_key]),
                'url_reply': URL(c='comments', f='comments_form.load', args=[owner_table, owner_key]),
                'url_list': URL(c='comments', f='comments_list.load', args=[owner_table, owner_key]),
                }
        comments += [SCRIPT(js, _type='text/javascript')]
        return DIV(comments, _id='comments_list')

    clist = get_comments(owner_table, owner_key)
    comments = html_comments(clist, False)
    return dict(comments=comments)


def comments_form():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    if not (owner_table and owner_key):
        response.view = 'others/gadget_error.html'        
        return dict(msg='comments dont work!')
    
    db.comments.owner_table.default = owner_table
    db.comments.owner_key.default = owner_key
    reply_key = request.vars.get('reply')
    if reply_key:
        db.comments.owner_table.default = 'comments'
        db.comments.owner_key.default = reply_key

    form = SQLFORM(db.comments)
    form.elements('#comments_comment_str')[0] ['_placeholder'] = T('Comment...') 
    form.elements('#comments_comment_str')[0] ['_style'] = 'width:100%;'

    if form.process().accepted:
        response.js = "web2py_component('%s','comments_list');" % URL(c='comments', f='comments_list.load', args=[owner_table, owner_key])

    return dict(form=form)


def comments_remove():
    owner_table = getlist(request.args, 0)
    owner_key  = getlist(request.args, 1)
    delete_id = request.vars.get('delete', 0)
    if delete_id:
        db(db.comments.id == delete_id).delete()    
        response.js = "web2py_component('%s','comments_list');" % URL(c='comments', f='comments_list.load', args=[owner_table, owner_key])
    pass
