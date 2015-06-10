/**
 * Expression in computing sum squared error for perspective transformation
 *
 * Description:
 */

const NUM_POINTS = 10

number focal : nodiff
vector centerOffset(2) : nodiff
vector scalingFactor(2) : nodiff
vector cameraTranslation(3)
vector q(4)       // Quaternion

vector x(NUM_POINTS) : nodiff
vector y(NUM_POINTS) : nodiff
vector z(NUM_POINTS)

expr rotationMatrix =
  [[1.0 - 2 * (q[1] ^ 2 + q[2] ^ 2), 2 * (q[0] * q[1] - q[2] * q[3]), 2 * (q[0] * q[2] + q[1] * q[3])],
   [2 * (q[0] * q[1] + q[2] * q[3]), 1.0 - 2 * (q[0] ^ 2 + q[2] ^ 2), 2 * (q[1] * q[2] - q[0] * q[3])],
   [2 * (q[0] * q[2] - q[1] * q[3]), 2 * (q[1] * q[2] + q[0] * q[3]), 1.0 - 2 * (q[0] ^ 2 + q[1] ^ 2)]]

expr main =
  for i in [0, NUM_POINTS - 1]
    sum(
      (x[i] - (focal * (([z[i] * x[i], z[i] * y[i], z[i]] - cameraTranslation)' * rotationMatrix * [1, 0, 0]) / (([z[i] * x[i], z[i] * y[i], z[i]] - cameraTranslation)' * rotationMatrix * [0, 0, 1]) * scalingFactor[0] + centerOffset[0])) ^ 2 +
      (y[i] - (focal * (([z[i] * x[i], z[i] * y[i], z[i]] - cameraTranslation)' * rotationMatrix * [0, 1, 0]) / (([z[i] * x[i], z[i] * y[i], z[i]] - cameraTranslation)' * rotationMatrix * [0, 0, 1]) * scalingFactor[1] + centerOffset[1])) ^ 2
    )
