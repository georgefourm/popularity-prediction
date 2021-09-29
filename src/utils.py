def get_content_types(msg):
    """
    Returns a flat array of all content types of the message
    :param EmailMessage msg:
    :return:
    """
    all_types = []
    if msg.is_multipart():
        for sub_msg in msg.get_payload():
            all_types += get_content_types(sub_msg)
    else:
        all_types.append(msg.get_content_type())
    return all_types