# Hướng dẫn sử dụng Detectron 
Theo như [GETTING STARTED](https://github.com/facebookresearch/Detectron/blob/master/GETTING_STARTED.md) thì phần code mẫu để sử dụng từ model được train sẵn là: 

```
python2 tools/infer_simple.py \
    --cfg configs/12_2017_baselines/e2e_mask_rcnn_R-101-FPN_2x.yaml \
    --output-dir /tmp/detectron-visualizations \
    --image-ext jpg \
    --wts https://s3-us-west-2.amazonaws.com/detectron/35861858/12_2017_baselines/e2e_mask_rcnn_R-101-FPN_2x.yaml.02_32_51.SgT4y1cO/output/train/coco_2014_train:coco_2014_valminusminival/generalized_rcnn/model_final.pkl \
    demo
```

Về cơ bản mình chỉ cần quan tâm chữ "demo", chính là tham số truyền vô thư mục mà mình lưu ảnh, và "--output-dir /tmp/dectectron..." ở trên là truyền vô thư mục kết quả xuất ra. 

Để sử dụng cho mục đích nghiên cứu của nhóm mình thì file infer_simple.py của anh Tú cũng sẽ được add vào file README này sớm.