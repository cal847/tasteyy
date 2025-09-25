def build_comment_tree(comments):
    """
    Converts a flat list of comments into a nested tree structure
    """
    comment_dict = {c.id: c for c in comments}
    tree = []

    for comment in comments:
        if comment.parent_id is None:
            tree.append(comment)
        else:
            parent = comment_dict.get(comment.parent_id)
            if parent:
                if not hasattr(parent, 'replies'):
                    parent.replies = []
                parent.replies.append(comment)

    # Sort replies by created_at
    def sort_replies(node):
        if hasattr(node, 'replies'):
            node.replies.sort(key=lambda x: x.created_at)
            for reply in node.replies:
                sort_replies(reply)
    
    for top in tree:
        sort_replies(top)

    return sorted(tree, key=lambda x: x.created_at)