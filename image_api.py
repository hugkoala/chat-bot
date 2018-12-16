import os
import uuid
import requests


class UserAssert:
    """
    Attributes:
        user_id: the user id of FB

    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.create_folder()

    def get_folder_path(self):
        """
            Get the path of user assert folder
        """

        return os.getcwd() + '/assert/' + self.user_id

    def create_folder(self):
        path = os.getcwd() + '/assert/' + self.user_id
        print(os.path.exists(path))
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            raise OSError

    def download_picture(self, image_url):
        """
            download image by image_url
        :param image_url: the url of image
        """
        image_request = requests.get(image_url)
        with open(self.get_folder_path() + '/' + str(uuid.uuid4()) + '.jpg', 'wb') as handler:
            handler.write(image_request.content)


if __name__ == '__main__':
    assert1 = UserAssert('123456789')
    assert1.download_picture(
        'https://scontent.xx.fbcdn.net/v/t1.15752-9/48085577_486101348464370_2818694466934669312_n.png?_nc_cat=107&_nc_ad=z-m&_nc_cid=0&_nc_ht=scontent.xx&oh=040f5983ff1594eaf34ff770f7c56ec3&oe=5C98F062')
