public class ChocolateDistribution {
    static int findMinDiff(int arr[], int n, int m) {
        if (m == 0 || n == 0)
            return 0;
            
        if (n < m)
            return -1;
            
        Arrays.sort(arr);
        
        int minDiff = arr[n-1] - arr[0];
        
        for (int i = 0; i <= n - m; i++) {
            minDiff = Math.min(minDiff, arr[i + m - 1] - arr[i]);
        }
        
        return minDiff;
    }
    
    public static void main(String[] args) {
        int arr[] = {12, 4, 7, 9, 2, 23, 25, 41, 30, 40, 28, 42, 30, 44, 48, 43, 50};
        int m = 7;
        int n = arr.length;
        
        System.out.println("Minimum difference is " + findMinDiff(arr, n, m));
    }
}