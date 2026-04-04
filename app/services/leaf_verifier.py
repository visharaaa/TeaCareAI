import torch
from PIL import Image
import clip
import os

class LeafVerifier:
    def __init__(self, positive_labels, negative_labels, imgPath, threshold=0.5, model="ViT-B/32"):
        self.imgPath = imgPath
        self.threshold = threshold
        self.num_positive = len(positive_labels)
        self.labels = positive_labels + negative_labels
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model, self.preprocess = clip.load(model, device=self.device)
        self.model.eval()
        self.text_tokens = clip.tokenize(self.labels).to(self.device)

    def is_tea_leaf(self, img):
        path = os.path.join(self.imgPath, img)
        image = self.preprocess(Image.open(path).convert("RGB"))
        image = image.unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits_per_image, _ = self.model(image, self.text_tokens)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

        scores = dict(zip(self.labels, probs))

        tea_prob = probs[:self.num_positive].sum()
        is_tea = bool(tea_prob >= self.threshold)
        return is_tea





# if __name__ == "__main__":
#     leaf_verifier= LeafVerifier(
#         positive_labels=[
#             "a tea leaf",
#             "tea plant leaves",
#             "a close up of a tea leaf",
#         ],
#         negative_labels=[
#             # People & body parts
#             "a human face",
#             "a person",
#             "a hand",
#             "a body part",
#             "a crowd of people",
#
#             # Animals
#             "an animal",
#             "a dog",
#             "a cat",
#             "a bird",
#             "an insect",
#
#             # Vehicles & transport
#             "a car or vehicle",
#             "a motorcycle",
#             "a truck",
#             "an airplane",
#             "a boat",
#
#             # Indoor objects & furniture
#             "indoor furniture",
#             "a chair or table",
#             "a bed or sofa",
#             "a lamp or light fixture",
#             "a shelf or cabinet",
#
#             # Food & drink
#             "food or drink",
#             "a fruit or vegetable",
#             "a cup or bottle",
#             "cooked or prepared food",
#             "a snack or dessert",
#
#             # Documents & screens
#             "a document or paper",
#             "a book or magazine",
#             "a phone or computer screen",
#             "a printed label or sign",
#             "a whiteboard or chalkboard",
#
#             # Outdoor non-plant scenes
#             "a building or structure",
#             "a road or pavement",
#             "a sky or cloud",
#             "a body of water",
#             "a mountain or rock",
#
#             # Miscellaneous objects
#             "a tool or machine",
#             "a plastic object",
#             "a fabric or clothing",
#             "a bag or container",
#             "electronic equipment",
#         ],
#         imgPath='test/'
#     )
#     print(leaf_verifier.is_tea_leaf("20260404_162351_IMG-20260404-WA0006.jpg"))

