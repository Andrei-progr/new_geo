from PIL import Image
import os
import torch
import numpy as np
import torchvision.transforms as transforms
from torchvision.models.segmentation.deeplabv3 import DeepLabHead
import torchvision.models as models
import pytorch_lightning as pl
import cv2
import gc

def script_method(fn, _rcb=None):
    return fn

def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj

script_method1 = torch.jit.script_method
script1 = torch.jit.script_if_tracing
torch.jit.script_method = script_method
torch.jit.script = script


class SegModel(pl.LightningModule):
    def __init__(self):
        super(SegModel, self).__init__()
        self.model = models.segmentation.deeplabv3_resnet50(weights='COCO_WITH_VOC_LABELS_V1')
        self.model.classifier = DeepLabHead(2048, 4)

    def forward(self, x):
        x = self.model(x)
        return x['out']


class ImagePrediction:
    def __init__(self, img):
        self.img = np.asarray(img)
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        # self.crops_512 = self.cropper(512)

        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda:0" if self.use_cuda else "cpu")
        torch.backends.cudnn.benchmark = True
        self.Transform = transforms.Compose([])
        self.destroyed = 0

    # Разбивает на квадратные изображения нужного размера
    def cropper(self, size):
        crops = []
        h = self.img.shape[0]
        w = self.img.shape[1]

        if w / h > 2:
            cr1 = self.img[:, :h]
            cr3 = self.img[:, w - h:w]
            cr2 = self.img[:, w // 2 - h // 2: w // 2 + h // 2]
            dim = (size, size)

            cr1 = cv2.resize(cr1, dim, interpolation=cv2.INTER_AREA)
            cr2 = cv2.resize(cr2, dim, interpolation=cv2.INTER_AREA)
            cr3 = cv2.resize(cr3, dim, interpolation=cv2.INTER_AREA)

            crops.append(cr1)
            crops.append(cr2)
            crops.append(cr3)

        if w / h < 2:
            cr1 = self.img[:, :h]
            cr2 = self.img[:, w - h:w]

            dim = (size, size)
            cr1 = cv2.resize(cr1, dim, interpolation=cv2.INTER_AREA)
            cr2 = cv2.resize(cr2, dim, interpolation=cv2.INTER_AREA)

            crops.append(cr1)
            crops.append(cr2)
        return crops

    def new_cropper(self, size):
        crops = []
        h = self.img.shape[0]
        w = self.img.shape[1]

        k = w // h
        for i in range(k):
            cr = self.img[:, i * h: (i + 1) * h]
            cr = cv2.resize(cr, (size, size), interpolation=cv2.INTER_AREA)
            crops.append(cr)
        cr = cv2.resize(self.img[:, w - h:], (size, size), interpolation=cv2.INTER_AREA)
        crops.append(cr)
        return crops

    def uncrop(self, crops, size=1024):
        h = self.img.shape[0]
        w = self.img.shape[1]
        k = w / h
        w = int(size * k)

        res = crops[0]
        l = len(crops) - 1
        for i in range(1, l):
            res = np.concatenate((res, crops[i]), axis=1)
        cr = crops[l][:, size - (w - (l * size)):]
        res = np.concatenate((res, cr), axis=1)
        return res

    def min_max(self, contour):
        y_points = []
        x_points = []
        for p in range(len(contour)):
            point = contour[p]
            y_points.append(point[0][1])
            x_points.append(point[0][0])
        y_points = np.array(y_points)
        x_points = np.array(x_points)
        return np.min(x_points), np.max(x_points), np.min(y_points), np.max(y_points)

    # Делает предсказание на одном кропе
    def PredictSingleCrop(self, cropp_img, model):

        Img = np.array([cropp_img[:, :, 2], cropp_img[:, :, 1], cropp_img[:, :, 0]])
        Img = torch.tensor(Img)
        Img = self.Transform(Img)
        Img = Img.unsqueeze(0).float()

        mask = model(Img.to(self.device))

        # Clearing GPU mem data
        gc.collect()
        torch.cuda.empty_cache()

        tensor_mask = torch.sigmoid(mask)
        numpy_mask = tensor_mask.detach().numpy()

        return numpy_mask[0][0]

    def DivideColumns(self, img, path, img_size=512):
        img = np.asarray(img)
        h = img.shape[0]
        w = img.shape[1]

        k = w / h
        size = k * img_size
        # label = np.zeros((img_size, int(size)))
        label = np.zeros((h, w))
        print(label.shape)
        for x in range(self.columns.shape[0]):
            for y in range(self.columns.shape[1]):
                if self.columns[x, y] > 125:
                    label[x, y] = 255
                else:
                    label[x, y] = 0
        label = label.astype(np.uint8)

        contours, hirerchy = cv2.findContours(label, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        label = cv2.cvtColor(label, cv2.COLOR_GRAY2BGR)
        for i in range(len(contours)):
            if hirerchy[0][i][3] != -1:
                cv2.fillPoly(label, [contours[i]], (255, 255, 255))

        label = cv2.cvtColor(label, cv2.COLOR_BGR2GRAY)
        contours, hirerchy = cv2.findContours(label, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

        im = cv2.resize(img, (int(size), img_size), interpolation=cv2.INTER_AREA)

        def minus(y, x):
            if y < x:
                return 0
            else:
                return y - x

        columns = []
        img_name = 1
        for i in range(len(hirerchy[0])):
            copy1 = np.copy(im)
            cv2.fillPoly(copy1, [contours[i]], (0, 0, 0))
            copy1 = im - copy1
            x_min, x_max, y_min, y_max = self.min_max(contours[i])
            copy2 = copy1[minus(y_min, 10): y_max + 10, minus(x_min, 10) : x_max + 10]
            columns.append(copy2)
            copy2 = cv2.rotate(copy2, cv2.ROTATE_90_CLOCKWISE)
            if copy2.shape[1] > 50:
                c = Image.fromarray(copy2)
                # b, g, r = c.split()
                # c = Image.merge("RGB", (r, g, b))
                c.save(path + str(img_name * 10) + ".png")
                img_name += 1
                # cv2.imwrite(path + str(i) + ".png", copy2)
        column_dir = os.listdir(path)
        try:
            column_dir.remove('mask.png')
        except:
            pass
        l = len(column_dir) + 1
        for i in range(1, l):
            os.rename(path + str(i * 10) + ".png", path + str(l - i) + ".png")

    def PredictDestroyed(self):
        model = torch.load(self.file_path + "\\Net\\model\\igt47(destroyed).pth", map_location=self.device)
        model.eval()
        crops = self.new_cropper(1024)
        masks = []

        for crop_1024 in crops:
            mask_1024 = self.PredictSingleCrop(crop_1024, model)
            masks.append(mask_1024)
        mask = self.uncrop(masks)
        mask = mask * 255
        self.destroyed = mask
        return mask

    def PredictProzhilki(self):
        model = torch.load(self.file_path + "\\Net\\model\\igt47zh.pth", map_location=self.device)
        model.eval()
        crops = self.new_cropper(1024)
        masks = []
        c = 1
        for crop_1024 in crops:
            mask_1024 = self.PredictSingleCrop(crop_1024, model)
            masks.append(mask_1024)
            c += 1
        mask = self.uncrop(masks)
        mask = mask * 255
        return mask

    def PredictCrack(self):
        model = torch.load(self.file_path + "\\Net\\model\\treshini34.pth", map_location=self.device)
        model.eval()
        crops = self.new_cropper(1024)
        masks = []
        c = 1
        for crop_1024 in crops:
            mask_1024 = self.PredictSingleCrop(crop_1024, model)
            masks.append(mask_1024)
            c += 1
        mask = self.uncrop(masks)
        mask = mask * 255
        return mask

    def PredictPoroda(self):
        h = self.img.shape[0]
        w = self.img.shape[1]
        k = w / h
        size = k * 1024

        model = torch.load(self.file_path + "\\Net\\model\\poroda.pth", map_location=self.device)
        model.eval()
        pic = cv2.resize(self.img, (1024, 1024), cv2.INTER_AREA)
        mask = self.PredictSingleCrop(pic, model)
        mask = cv2.resize(mask, (int(size), 1024), cv2.INTER_LINEAR)
        mask = mask * 255
        mask = mask - self.destroyed
        return mask

    def PredictColumns(self, path):
        model = torch.load(self.file_path + "\\Net\\model\\igt35 (columns).pth", map_location=self.device)
        # self.columns = self.Predict(model)
        # self.columns = self.columns * 255
        model.eval()
        crops = self.new_cropper(512)
        masks = []

        for crop_512 in crops:
            mask_512 = self.PredictSingleCrop(crop_512, model)
            masks.append(mask_512)
        mask = self.uncrop(masks, 512)
        mask = mask * 255
        self.columns = mask
        im = Image.fromarray(mask)
        im = im.convert("L")
        im.save(path + "\\cols.png")
        return self.columns


    def PredictLithotypes(self):
        h = self.img.shape[0]
        w = self.img.shape[1]
        k = w / h
        size = k * 700
        out_resize = transforms.Resize((700, int(size)))
        model = SegModel().to(self.device)
        model = model.load_from_checkpoint(self.file_path + "\\Net\\model\\epoch=18-step=1406.ckpt", map_location=self.device)
        model.eval()

        image = cv2.resize(self.img, (700, 700), cv2.INTER_LINEAR)
        image = torch.tensor(image).to(self.device).float().permute(2, 0, 1).unsqueeze(0)

        outputs = model(image)
        outputs = out_resize(outputs)
        predicted_masks = torch.argmax(outputs, dim=1)
        predicted_mask = predicted_masks.detach().numpy()
        predicted_mask = predicted_mask.transpose(1, 2, 0)
        predicted_mask *= 80
        return predicted_mask


    # Делает предсказание на всей картинке
    def Predict(self, model):
        masks = []
        model.eval()

        for crop_512 in self.crops_512:
            mask_512 = self.PredictSingleCrop(crop_512, model)
            masks.append(mask_512)

        mask = self.uncrop_512(masks)
        return mask
