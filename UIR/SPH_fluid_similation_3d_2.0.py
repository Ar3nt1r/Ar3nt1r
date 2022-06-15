import numpy as np
import matplotlib.pyplot as plt
from sklearn import neighbors
from tqdm import tqdm

MAX_PARTICLES = 200
DOMAIN_WIDTH = 40
DOMAIN_HEIGHT = 80

PARTICLE_MASS = 1
ISOTROPIC_EXPONENT = 20
BASE_DENSITY = 1
SMOOTHING_LENGTH = 4
DYNAMIC_VISCOSITY = 0.5
DAMPING_COEFFICIENT = - 0.9
#
CONSTANT_FORCE = np.array([[0.0, 0.0, -1.0]])

TIME_STEP_LENGTH = 0.01
N_TIME_STEPS = 2_500
ADD_PARTICLES_EVERY = 10

FIGURE_SIZE = (4, 4, 6)
PLOT_EVERY = 6
SCATTER_DOT_SIZE = 3_00

DOMAIN_X_LIM = np.array([
    SMOOTHING_LENGTH,
    DOMAIN_WIDTH - SMOOTHING_LENGTH,
])
DOMAIN_Z_LIM = np.array([
    SMOOTHING_LENGTH,
    DOMAIN_HEIGHT - SMOOTHING_LENGTH,
])

DOMAIN_Y_LIM = np.array([
    SMOOTHING_LENGTH,
    DOMAIN_WIDTH - SMOOTHING_LENGTH,
])

NORMALIZATION_DENSITY = (
        (
                315 * PARTICLE_MASS
        ) / (
                64 * np.pi * SMOOTHING_LENGTH ** 9
        )
)
NORMALIZATION_PRESSURE_FORCE = (
        -
        (
                45 * PARTICLE_MASS
        ) / (
                np.pi * SMOOTHING_LENGTH ** 6
        )
)
NORMALIZATION_VISCOUS_FORCE = (
        (
                45 * DYNAMIC_VISCOSITY * PARTICLE_MASS
        ) / (
                np.pi * SMOOTHING_LENGTH ** 6
        )
)


def main():
    n_particles = 1

    positions = np.zeros((n_particles, 3))
    velocities = np.zeros_like(positions)
    forces = np.zeros_like(positions)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    file = open('coords.xyz', 'w')

    for iter in tqdm(range(N_TIME_STEPS)):
        if iter % ADD_PARTICLES_EVERY == 0 and n_particles < MAX_PARTICLES:
            new_positions = np.array([
                [10 + np.random.rand(), DOMAIN_Y_LIM[1], DOMAIN_Z_LIM[1]],
                [15 + np.random.rand(), DOMAIN_Y_LIM[1], DOMAIN_Z_LIM[1]],
                [20 + np.random.rand(), DOMAIN_Y_LIM[1], DOMAIN_Z_LIM[1]]
            ])

            new_velocities = np.array([
                [-3.0, -3.0, -15.0],
                [-3.0, -3.0, -15.0],
                [-3.0, -3.0, -15.0],
            ])

            n_particles += 3

            positions = np.concatenate((positions, new_positions), axis=0)
            velocities = np.concatenate((velocities, new_velocities), axis=0)

        neighbor_ids, distances = neighbors.KDTree(
            positions,
        ).query_radius(
            positions,
            SMOOTHING_LENGTH,
            return_distance=True,
            sort_results=True,
        )

        densities = np.zeros(n_particles)

        for i in range(n_particles):
            for j_in_list, j in enumerate(neighbor_ids[i]):
                densities[i] += NORMALIZATION_DENSITY * (
                        SMOOTHING_LENGTH ** 2
                        -
                        distances[i][j_in_list] ** 2
                ) ** 3

        pressures = ISOTROPIC_EXPONENT * (densities - BASE_DENSITY)

        forces = np.zeros_like(positions)

        # Drop the element itself
        neighbor_ids = [np.delete(x, 0) for x in neighbor_ids]
        distances = [np.delete(x, 0) for x in distances]

        for i in range(n_particles):
            for j_in_list, j in enumerate(neighbor_ids[i]):
                # Pressure force
                forces[i] += NORMALIZATION_PRESSURE_FORCE * (
                        -
                        (
                                positions[j]
                                -
                                positions[i]
                        ) / distances[i][j_in_list]
                        *
                        (
                                pressures[j]
                                +
                                pressures[i]
                        ) / (2 * densities[j])
                        *
                        (
                                SMOOTHING_LENGTH
                                -
                                distances[i][j_in_list]
                        ) ** 2
                )

                # Viscous force
                forces[i] += NORMALIZATION_VISCOUS_FORCE * (
                        (
                                velocities[j]
                                -
                                velocities[i]
                        ) / densities[j]
                        *
                        (
                                SMOOTHING_LENGTH
                                -
                                distances[i][j_in_list]
                        )
                )

        # Force due to gravity
        forces += CONSTANT_FORCE

        # Euler Step
        velocities = velocities + TIME_STEP_LENGTH * forces / densities[:, np.newaxis]
        positions = positions + TIME_STEP_LENGTH * velocities

        # Enfore Boundary Conditions
        out_of_left_boundary = positions[:, 0] < DOMAIN_X_LIM[0]
        out_of_right_boundary = positions[:, 0] > DOMAIN_X_LIM[1]

        out_of_front_boundary = positions[:, 1] < DOMAIN_Y_LIM[0]
        out_of_back_boundary = positions[:, 1] > DOMAIN_Y_LIM[1]

        out_of_bottom_boundary = positions[:, 2] < DOMAIN_Z_LIM[0]
        out_of_top_boundary = positions[:, 2] > DOMAIN_Z_LIM[1]

        velocities[out_of_left_boundary, 0] *= DAMPING_COEFFICIENT
        positions[out_of_left_boundary, 0] = DOMAIN_X_LIM[0]

        velocities[out_of_right_boundary, 0] *= DAMPING_COEFFICIENT
        positions[out_of_right_boundary, 0] = DOMAIN_X_LIM[1]

        velocities[out_of_front_boundary, 1] *= DAMPING_COEFFICIENT
        positions[out_of_front_boundary, 1] = DOMAIN_Y_LIM[0]

        velocities[out_of_back_boundary, 1] *= DAMPING_COEFFICIENT
        positions[out_of_back_boundary, 1] = DOMAIN_Y_LIM[1]

        velocities[out_of_bottom_boundary, 2] *= DAMPING_COEFFICIENT
        positions[out_of_bottom_boundary, 2] = DOMAIN_Z_LIM[0]

        velocities[out_of_top_boundary, 2] *= DAMPING_COEFFICIENT
        positions[out_of_top_boundary, 2] = DOMAIN_Z_LIM[1]

        if iter % PLOT_EVERY == 0:
            ax.scatter(positions[:, 0],
                       positions[:, 1],
                       positions[:, 2],
                       s=SCATTER_DOT_SIZE,
                       c=positions[:, 2],
                       cmap="Wistia_r"
                       )
            ax.set(
                xticks=[],
                yticks=[],
                zticks=[],

            )

            # Writing to the file

            file.write(str(len(positions)) + 2 * '\n')
            for i in range(len(positions)):
                file.write(str(i) + ' ')
                for j in range(3):
                    file.write(str(positions[i][j]) + ' ')
                file.write('\n')
    file.close()


if __name__ == "__main__":
    main()

