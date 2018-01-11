figure
load '../label_stats_D110_S10.csv'
subplot(3,1,1)
hist(label_stats_D110_S10(1,:), 20)
grid on
xlabel('label ratio')
ylabel('user count')
title('dist thres=0.001~110m s=10km/h')

subplot(3,1,2)
hist(label_stats_D110_S10(2,:), 20)
grid on
xlabel('double label ratio')
ylabel('user count')


subplot(3,1,3)
hist(label_stats_D110_S10(3,:), 20)
grid on
xlabel('label ratio (no home)')
ylabel('user count')


figure
load '../label_stats_D220_S5.csv'
subplot(3,1,1)
hist(label_stats_D220_S5(1,:), 20)
grid on
xlabel('label ratio')
ylabel('user count')
title('dist thres=0.001~220m s=5km/h')

subplot(3,1,2)
hist(label_stats_D220_S5(2,:), 20)
grid on
xlabel('double label ratio')
ylabel('user count')


subplot(3,1,3)
hist(label_stats_D220_S5(3,:), 20)
grid on
xlabel('label ratio (no home)')
ylabel('user count')



figure
load '../prepare_stats.csv'
subplot(4,1,1)
hist(prepare_stats(1, :), 20)
grid on
xlabel('overlap / has nearby')
ylabel('user count')

subplot(4,1,2)
hist(prepare_stats(2, :), 20)
grid on
xlabel('has nearby / total')
ylabel('user count')


subplot(4,1,3)
hist(prepare_stats(3, :), 20)
grid on
xlabel('has 2 nearbys / total')
ylabel('user count')

subplot(4,1,4)
hist(prepare_stats(4, :), 20)
grid on
xlabel('has 5 nearbys / total')
ylabel('user count')


