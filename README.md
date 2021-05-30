# Attr-Hyperparams
Easy parameter specification using dataclasses made using the [attr](https://www.attrs.org/en/stable/) library. It comes with following advantages compared to other parametrisation schemes (eg. jsons)

1.  No KeyErrors
2.  Typed
3.  Default values so only need to specify changes - (compared this to maintaining tons of json files for each configuration)
4.  All attr features for free. Eg. validators, comparators etc.
5.  Intellisense in ide
6.  Both dict-like and dot access
7.  Interconversion to/from dict as well as flattened dict
8.  Easy De/serialisation from/to json and yaml.
9.  Direct instantiation of objects from parameters specifying constructor arguments.
10. Flexible + automatic disambiguation
11. Easy hyper-parameter search
12. And last but not the least, almost no overhead!

See [this notebook](https://github.com/Shivanshu-Gupta/attr-hyperparams/blob/main/sample_param_usage.ipynb) for examples of usage and features.
