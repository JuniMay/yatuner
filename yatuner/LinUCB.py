from random import randint
from typing import Union
import numpy as np


class LinUCB:

    def __init__(self, dimension, arms, alpha=0.25, nth_choice=1) -> None:
        self.alpha = alpha
        self.dimension = dimension
        self.Aa = {}
        self.AaI = {}
        self.ba = {}
        self.theta = {}
        self.a_max = 0
        self.arms = arms
        self.x = None
        self.xT = None
        self.nth_choice = nth_choice

    def init(self) -> None:
        for arm in self.arms:
            self.Aa[arm] = np.identity(self.dimension)
            self.AaI[arm] = np.identity(self.dimension)
            self.ba[arm] = np.zeros((self.dimension, 1))
            self.theta[arm] = np.zeros((self.dimension, 1))

    def recommend(self, usr_features) -> Union[int, float]:
        assert len(usr_features
                   ) == self.dimension, "usr_features's dimension dismatch"
        xaT = np.array([usr_features])
        xa = np.transpose(xaT)

        AaI_t = np.array([self.AaI[arm] for arm in self.arms])
        theta_t = np.array([self.theta[arm] for arm in self.arms])
        pta = np.dot(xaT, theta_t) + self.alpha * np.sqrt(
            np.dot(np.dot(xaT, AaI_t), xa))
        if self.nth_choice > 1:
            order = np.argsort(pta.flatten())[::-1]
            choice = self.arms[order[randint(0, self.nth_choice - 1)]]
        else:
            choice = self.arms[np.argmax(pta)]

        self.x = xa
        self.xT = xaT
        self.a_max = choice
        return choice

    def update(self, reward) -> None:
        self.Aa[self.a_max] += np.dot(self.x, self.xT)
        self.ba[self.a_max] += reward * self.x
        self.AaI[self.a_max] = np.linalg.solve(self.Aa[self.a_max],
                                               np.identity(self.dimension))
        self.theta[self.a_max] = np.dot(self.AaI[self.a_max],
                                        self.ba[self.a_max])
