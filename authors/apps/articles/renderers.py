from rest_framework import renderers
import json


class ArticlesRenderer(renderers.BaseRenderer):
    """This class determines how the articles should be displayed"""
    media_type = 'application/json'
    format = 'json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """This method overwrites the current render method"""
        # checks if the data received is a list
        if isinstance(data, list):
            # converts it into a dictionary with a key
            return json.dumps(
                {
                    'status': 'success',
                    'articles': data
                }
            )
        else:
            # checks if the data received is an error message
            error = data.get('detail')
            if error:
                return json.dumps(
                    {
                        'status': 'error',
                        'message': data
                    }
                )
            else:
                # if not an error then it must be a single article dictionary
                return json.dumps(
                    {
                        'status': 'success',
                        'article': data
                    }
                )


